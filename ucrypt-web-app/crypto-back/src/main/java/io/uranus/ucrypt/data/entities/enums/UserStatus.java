package io.uranus.ucrypt.data.entities.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
@Getter
public enum UserStatus {

    CREATED("created", "Created"),
    ACTIVE("active", "Active"),
    INACTIVE("inactive", "InActive");
    private String name;

    private String displayName;

}
