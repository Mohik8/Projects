package org.uranus.data;

import org.uranus.model.UserModel;
import org.uranus.model.UserRegistrationModel;

public class UranusFaker {
    public static String getRandomEmail() {
        return "test" + System.currentTimeMillis() + "@example.com";
    }

    public static String getRandomPassword() {
        return "password" + System.currentTimeMillis();
    }

    public static String getRandomName() {
        return "User" + System.currentTimeMillis();
    }

    public static UserRegistrationModel getRandomBaseUserRegistration() {
        return UserRegistrationModel.builder()
                .email(getRandomEmail())
                .password(getRandomPassword())
                .name(getRandomName())
                .confirmPassword(getRandomPassword()) // Will be overwritten below
                .build();
    }

    public static UserRegistrationModel getRandomUserRegistration() {
        UserRegistrationModel user = getRandomBaseUserRegistration();
        return UserRegistrationModel.builder()
                .email(user.email)
                .password(user.password)
                .name(user.name)
                .confirmPassword(user.password) // Confirm password should match
                .role("USER")
                .build();
    }

    public static UserRegistrationModel getRandomAdminRegistration() {
        UserRegistrationModel user = getRandomBaseUserRegistration();
        return UserRegistrationModel.builder()
                .email(user.email)
                .password(user.password)
                .name(user.name)
                .confirmPassword(user.password)
                .role("ADMIN")
                .build();
    }

    public static UserRegistrationModel getRandomEmployeeRegistration() {
        UserRegistrationModel user = getRandomBaseUserRegistration();
        return UserRegistrationModel.builder()
                .email(user.email)
                .password(user.password)
                .name(user.name)
                .confirmPassword(user.password)
                .role("EMPLOYEE")
                .build();
    }

    private static UserModel getRandomBaseUser() {
        return UserModel.builder()
                .email(getRandomEmail())
                .password(getRandomPassword())
                .name(getRandomName())
                .build();
    }
    
    public static UserModel getRandomUser() {
        UserModel user = getRandomBaseUser();
        return UserModel.builder()
                .email(user.email)
                .password(user.password)
                .name(user.name)
                .role("USER")
                .build();
    }

    public static UserModel getRandomAdmin() {
        UserModel user = getRandomBaseUser();
        return UserModel.builder()
                .email(user.email)
                .password(user.password)
                .name(user.name)
                .role("ADMIN")
                .build();
    }

    public static UserModel getRandomEmployee() {
        UserModel user = getRandomBaseUser();
        return UserModel.builder()
                .email(user.email)
                .password(user.password)
                .name(user.name)
                .role("EMPLOYEE")
                .build();
    }
}
