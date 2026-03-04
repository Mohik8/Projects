Feature: Password Strength 
    Scenario: User Enters a Super Strong Password 
        Given I am a new user on the sign up page for password strength
        When I enter a Super Strong password  
        Then I should be able to see that the password Strength bar is blue, and says Super Strong  

    Scenario: User Enters a weak Password
        Given I am a new user on the sign up page for password strength
        When I enter a weak password  
        Then I should be able to see that the password Strength bar is red, and says weak  

    Scenario: User Enters a Medium Password 
        Given I am a new user on the sign up page for password strength
        When I enter a Medium password  
        Then I should be able to see that the password Strength bar is yellow, and says Medium  

    Scenario: User Enters a Strong Password 
        Given I am a new user on the sign up page for password strength
        When I enter a Strong password  
        Then I should be able to see that the password Strength bar is green, and says Strong  