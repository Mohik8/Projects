package org.uranus.model;

import lombok.Builder;

@Builder
public class UserRegistrationModel {
    public String name;
    public String email;
    public String password;
    public String confirmPassword;
    public String role;
}