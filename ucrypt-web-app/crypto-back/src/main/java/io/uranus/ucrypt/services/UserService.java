package io.uranus.ucrypt.services;

import io.uranus.ucrypt.api.v1.resources.*;
import io.uranus.ucrypt.data.entities.User;
import io.uranus.ucrypt.data.entities.enums.UserStatus;
import io.uranus.ucrypt.data.repositories.RoleRepository;
import io.uranus.ucrypt.data.repositories.UserRepository;
import io.uranus.ucrypt.security.JwtGenerator;
import io.uranus.ucrypt.services.exceptions.BusinessException;
import io.uranus.ucrypt.services.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final AuthenticationManager authenticationManager;
    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtGenerator jwtGenerator;
    private final User currentUser;

    /**
     * Returns details of the current user that is making this request.
     *
     * @return details of the current user.
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'EMPLOYEE', 'USER')")
    @Transactional(readOnly = true)
    public UserDetailsResource getCurrentUserDetails() {
        return this.userMapper.map(this.currentUser);
    }

    /**
     * Creates a new user with status = 'CREATED' if user doesn't already exist and password is valid,
     * also create employee entity if role is employee.
     *
     * @param userRequestResource -> name: name of the new user,
     *                            email: email of the new user,
     *                            password: password that will be used to authenticate the new user,
     *                            role: role which will be first assigned to the new user.
     * @throws BusinessException 400 if {@code userRequestResource.email} is not in a valid email regex;
     *                           or if email already used for another user;
     *                           or if password is not a valid password;
     *                           or if jobTitle is null or empty when role is employee;
     */
    @Transactional
    public void register(final RegisterUserRequestResource userRequestResource) {
        validateUserAlreadyExists(userRequestResource);
        validatePasswordIsValid(userRequestResource.getPassword());
        final var user = constructUser(userRequestResource);
        this.userRepository.save(user);
    }

    private void validatePasswordIsValid(final String password) {
        if (password == null || password.isBlank() || password.length() < 6 || password.length() > 24) {
            throw new BusinessException(HttpStatus.BAD_REQUEST, "password length must be between 6 and 24");
        }
    }

    private void validateUserAlreadyExists(final RegisterUserRequestResource userRequestResource) {
        if (this.userRepository.existsByEmail(userRequestResource.getEmail())) {
            throw new BusinessException(HttpStatus.BAD_REQUEST, "user with this email already exists");
        }
    }

    private User constructUser(final RegisterUserRequestResource userRequestResource) {
        final var user = this.userMapper.map(userRequestResource);
        final var role = this.roleRepository.findByName(userRequestResource.getRole().name())
                .orElseThrow(() -> new BusinessException(
                        HttpStatus.BAD_REQUEST, String.format("role with name = %s doesn't exist", userRequestResource.getRole().name()))
                );
        final var encodedPassword = this.passwordEncoder.encode(userRequestResource.getPassword());

        user.setRole(role);
        user.setPassword(encodedPassword);
        user.setStatus(UserStatus.CREATED);

        return user;
    }


    /**
     * Returns the logged-in user data and token which will be used to authenticate the other requests,
     * by using the email and password that are passed we identify the user and check if he can be
     * authenticated or not and if he's generate a jwt token and return it with the user data.
     *
     * @param loginUserRequestResource -> email: email of the user,
     *                                 password: password of the user.
     * @return the logged-in user data and his jwt token.
     * @throws BusinessException 401 if {@code userRequestResource.email} and {@code userRequestResource.password}
     *                           aren't correct;
     *                           or if user isn't active to authenticate entry;
     */
    @Transactional
    public LoginUserResponseResource login(final LoginUserRequestResource loginUserRequestResource) {
        final var user = this.userRepository.findByEmail(loginUserRequestResource.getEmail()).get();
        final var authToken = new UsernamePasswordAuthenticationToken(loginUserRequestResource.getEmail(),
                loginUserRequestResource.getPassword());
        final Authentication authentication = this.authenticationManager.authenticate(authToken);
        SecurityContextHolder.getContext().setAuthentication(authentication);
        final String token = this.jwtGenerator.generateToken(authentication);

        return new LoginUserResponseResource()
                .name(user.getName())
                .accessToken(token);
    }

    /**
     * Returns a paginated result of users that are in the system based on the pageable object which defines
     * how many rows does a page contain, the page number that should be return and how will the page will be sorted,
     * and the specificationFrom which will filter the data based on specific conditions.
     *
     * @param specificationFrom specification used to filter the data
     * @param pageOf            pageable used to paginate the data
     * @return page of users
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'USER')")
    @Transactional
    public Page<UserListResource> getUsers(final Specification<User> specificationFrom, final Pageable pageOf) {
        final var users = this.userRepository.findAll(specificationFrom, pageOf);
        return users.map(this.userMapper::mapToUserList);
    }

    /**
     * Activates a user using the user id which is passed as a parameter.
     *
     * @param userId -> user id.
     * @throws BusinessException 404 if user can't be found.
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'USER')")
    @Transactional
    public void activateUser(final Long userId) {
        final var user = this.userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND));
        user.setStatus(UserStatus.ACTIVE);
        this.userRepository.save(user);
    }

    /**
     * Deactivates a user using the user id which is passed as a parameter.
     *
     * @param userId -> user id.
     * @throws BusinessException 404 if user can't be found.
     */
    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public void deactivateUser(final Long userId) {
        final var user = this.userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND));
        user.setStatus(UserStatus.INACTIVE);
        this.userRepository.save(user);
    }

    /**
     * Changes a user role using his id and what will his new role be as parameters.
     *
     * @param id                            -> user id.
     * @param updateUserRoleRequestResource -> user is new role.
     * @throws BusinessException 404 if user can't be found.
     * @throws BusinessException 400 if new role is not a valid role.
     */
    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public void updateUserRole(final Long id, final UpdateUserRoleRequestResource updateUserRoleRequestResource) {
        final var user = this.userRepository.findById(id)
                .orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND, String.format("There's no user with id %s", id)));
        final var role = this.roleRepository.findByName(updateUserRoleRequestResource.getNewRole().name())
                .orElseThrow(() -> new BusinessException(HttpStatus.BAD_REQUEST,
                        String.format("There's no role with name %s", updateUserRoleRequestResource.getNewRole().name())));

        user.setRole(role);
        this.userRepository.save(user);
    }
}
