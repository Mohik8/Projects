package io.uranus.ucrypt.services;

import io.uranus.ucrypt.api.v1.resources.RoleResource;
import io.uranus.ucrypt.data.repositories.RoleRepository;
import io.uranus.ucrypt.services.mapper.RoleMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class RoleService {

    private final RoleRepository roleRepository;

    private final RoleMapper roleMapper;

    /**
     * Returns a list of roles that can be assigned to new users.
     *
     * @return list of roles.
     */
    public List<RoleResource> getRolesForNewUsers() {
        final var roles = this.roleRepository.findAll();
        return roles.stream()
                .map(this.roleMapper::map)
                .collect(Collectors.toList());
    }
}
