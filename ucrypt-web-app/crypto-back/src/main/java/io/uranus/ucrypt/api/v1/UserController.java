package io.uranus.ucrypt.api.v1;

import io.uranus.ucrypt.api.v1.resources.*;
import io.uranus.ucrypt.services.EncryptionKeyService;
import io.uranus.ucrypt.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class UserController extends AbstractController implements UsersApi {

    private final UserService userService;

    private final EncryptionKeyService encryptionKeyService;

    @Override
    public ResponseEntity<Void> register(final RegisterUserRequestResource registerUserRequestResource) {
        this.userService.register(registerUserRequestResource);
        return ResponseEntity.status(HttpStatus.CREATED)
                .build();
    }


    @Override
    public ResponseEntity<LoginUserResponseResource> login(final LoginUserRequestResource loginUserRequestResource) {
        return ResponseEntity
                .ok()
                .body(this.userService.login(loginUserRequestResource));
    }

    @Override
    public ResponseEntity<UserDetailsResource> getCurrentUserDetails() {
        return ResponseEntity
                .ok()
                .body(this.userService.getCurrentUserDetails());
    }

    @Override
    public ResponseEntity<List<UserListResource>> getUsers(final Integer offset, final Integer limit, final String sort, final String filter) {
        final var usersPage = this.userService.getUsers(specificationFrom(filter), pageOf(offset, limit, sortBy(sort)));
        return ResponseEntity.ok()
                .header(TOTAL_COUNT_HEADER, String.valueOf(usersPage.getTotalElements()))
                .header(TOTAL_PAGES_COUNT_HEADER, String.valueOf(usersPage.getTotalPages()))
                .body(usersPage.getContent());
    }

    @Override
    public ResponseEntity<Void> activateUser(final Long userId) {
        this.userService.activateUser(userId);
        return ResponseEntity.ok()
                .build();
    }

    @Override
    public ResponseEntity<Void> deactivateUser(final Long userId) {
        this.userService.deactivateUser(userId);
        return ResponseEntity.ok()
                .build();
    }

    @Override
    public ResponseEntity<Void> createEncryptionKeyForCurrentUser(final CreateEncryptionKeyResource createEncryptionKeyResource) {
        this.encryptionKeyService.createEncryptionKeyForCurrentUser(createEncryptionKeyResource);
        return ResponseEntity.ok()
                .build();
    }

    @Override
    public ResponseEntity<List<EncryptionKeyListResource>> getCurrentUserEncryptionKeys(final Integer offset,
                                                                                        final Integer limit,
                                                                                        final String sort,
                                                                                        final String filter) {
        final var usersPage = this.encryptionKeyService.getEncryptionKeysForCurrentUser(specificationFrom(filter), pageOf(offset, limit, sortBy(sort)));
        return ResponseEntity.ok()
                .header(TOTAL_COUNT_HEADER, String.valueOf(usersPage.getTotalElements()))
                .header(TOTAL_PAGES_COUNT_HEADER, String.valueOf(usersPage.getTotalPages()))
                .body(usersPage.getContent());
    }

    @Override
    public ResponseEntity<Void> updateUserRole(final Long id, final UpdateUserRoleRequestResource updateUserRoleRequestResource) {
        this.userService.updateUserRole(id, updateUserRoleRequestResource);
        return ResponseEntity.ok()
                .build();
    }
}
