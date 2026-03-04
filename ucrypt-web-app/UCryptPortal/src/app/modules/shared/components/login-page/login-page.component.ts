import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { LoginRequest } from 'src/app/models/user/login/login-request';
import { AccountService } from 'src/app/services/account.service';
import { AuthService } from 'src/app/services/auth.service';
import { RoleService } from 'src/app/services/role.service';

@Component({
  selector: 'app-login-page',
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.scss']
})
export class LoginPageComponent implements OnInit {
  loginForm!: FormGroup;
  loginRequest!: LoginRequest;
  submitted:boolean = false;

  showSignup: boolean= false;
  @ViewChild('loginCloseBtn') loginCloseBtn?: ElementRef;

  constructor(
    private accountService: AccountService,
    protected authService: AuthService,
    private roleService: RoleService,
    private spinnerService: NgxSpinnerService,
    private messageService: MessageService
  ){

  }

  ngOnInit(): void {
      this.createLoginForm();
  }

  private createLoginForm() {
    this.loginForm = new FormGroup({
      email: new FormControl<string>('', [Validators.required, Validators.email]),
      password: new FormControl<string>('', [Validators.required, Validators.minLength(6), Validators.maxLength(24)])
    });
  }

  onLoginSumbit() {
    this.submitted= true;
    if (this.loginForm.valid) {
      this.loginRequest = {
        ...this.loginForm.value
      };
      this.spinnerService.show();
      this.accountService.login(this.loginRequest).subscribe({
        next: (response) => {
          this.submitted= false;

            this.spinnerService.hide();
          this.messageService.add({severity:'success', detail: 'User ' + response.name +' Logged in successfully'});
          this.loginCloseBtn?.nativeElement.click();
        },
        error: (error) => {
            this.spinnerService.hide();

          if (error.error?.message) {
            this.messageService.add({severity:'error', detail: error.error.message});
          } else if (error.status === 401) {
            this.messageService.add({severity:'error', detail: "Invalid credentials!"})
          }
        }
      });
    }
  }
}
