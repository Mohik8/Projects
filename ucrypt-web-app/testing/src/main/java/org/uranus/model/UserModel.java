package org.uranus.model;

import lombok.Builder;

// Represent a user in the Uranus system during testing
@Builder
public class UserModel {
    public String password;
    public String email;
    public String name;
    public String role;
}
