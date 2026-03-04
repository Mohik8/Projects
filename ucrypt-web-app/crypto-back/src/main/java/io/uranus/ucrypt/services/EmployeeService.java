package io.uranus.ucrypt.services;

import io.uranus.ucrypt.api.v1.resources.EmployeesListResource;
import io.uranus.ucrypt.data.entities.Role;
import io.uranus.ucrypt.data.entities.User;
import io.uranus.ucrypt.data.entities.enums.UserStatus;
import io.uranus.ucrypt.data.repositories.UserRepository;
import io.uranus.ucrypt.services.mapper.EmployeeMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class EmployeeService {

    private final UserRepository userRepository;

    private final EmployeeMapper employeeMapper;

    /**
     * Returns a list of users with role employee and active
     *
     * @return List of users with role employee and are active
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'EMPLOYEE', 'USER')")
    @Transactional(readOnly = true)
    public Page<EmployeesListResource> getEmployees(Specification<User> specificationFrom, Pageable pageOf) {
        final var modifiedSpecification = specificationFrom.and(this.filterByRoleEmployee()).and(this.filterByActiveStatus());
        final var employees = this.userRepository.findAll(modifiedSpecification, pageOf);
        return employees.map(this.employeeMapper::map);
    }

    private Specification<User> filterByActiveStatus() {
        return (root, query, criteriaBuilder) ->
                criteriaBuilder.equal(root.get("status"), UserStatus.ACTIVE);    }

    private Specification<User> filterByRoleEmployee() {
        return (root, query, criteriaBuilder) ->
                criteriaBuilder.equal(root.get("role").get("name"), Role.RoleProperty.EMPLOYEE.getName());
    }
}
