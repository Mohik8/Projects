Feature: Resources Tab Uploader
    Scenario: Admin uploads a resource
        Given I am signed in as an admin user
        And I navigate to the resource section of the admin panel
        And I click “Choose” to upload a file
        Then the uploaded file is shown as a preview
        When I click “Upload”
        Then the file is uploaded to the server and appears in the uploaded downloads
    
    Scenario: Admin cancels process during upload
        Given I am signed in as an admin user
        And I navigate to the resource section of the admin panel
        And I click “Choose” to upload a file
        Then the uploaded file is shown as a preview
        When I click the “Cancel” button
        Then the staged file is removed from the preview