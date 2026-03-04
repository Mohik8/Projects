package io.uranus.ucrypt.data.constants;

import io.uranus.ucrypt.data.entities.Role;

import java.util.Collection;
import java.util.List;

public class RoleConstants {

    public static final Collection<String> NEW_USER_ROLES = List.of(Role.RoleProperty.USER.getName(), Role.RoleProperty.EMPLOYEE.getName());
}
