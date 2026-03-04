package io.uranus.ucrypt.services.mapper;

import io.uranus.ucrypt.api.v1.resources.RegisterUserRequestResource;
import io.uranus.ucrypt.api.v1.resources.UserDetailsResource;
import io.uranus.ucrypt.api.v1.resources.UserListResource;
import io.uranus.ucrypt.data.entities.User;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring")
public interface UserMapper {

    UserDetailsResource map(User user);

    UserListResource mapToUserList(User user);

    @Mapping(target = "role", ignore = true)
    @Mapping(target = "password", ignore = true)
    User map(RegisterUserRequestResource registerResource);
}
