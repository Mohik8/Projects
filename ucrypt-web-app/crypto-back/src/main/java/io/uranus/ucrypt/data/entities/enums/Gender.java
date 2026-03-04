package io.uranus.ucrypt.data.entities.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
@Getter
public enum Gender {

    MALE("male", "Male"),
    FEMALE("female", "Female");

    private String name;

    private String displayName;

}
