package io.uranus.ucrypt.services.mapper;

import io.uranus.ucrypt.api.v1.resources.EmployeesListResource;
import io.uranus.ucrypt.data.entities.User;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring")
public interface EmployeeMapper {

    @Mapping(target = "employeeId", source = "id")
    EmployeesListResource map(User user);
}
