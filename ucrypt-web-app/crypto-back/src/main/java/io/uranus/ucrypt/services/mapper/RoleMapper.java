package io.uranus.ucrypt.services.mapper;

import io.uranus.ucrypt.api.v1.resources.RoleResource;
import io.uranus.ucrypt.data.entities.Role;
import org.mapstruct.Mapper;

import java.util.List;

@Mapper(componentModel = "spring")
public interface RoleMapper {

    RoleResource map(Role role);

    List<RoleResource> map(List<Role> roles);
}
