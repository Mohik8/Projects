import { AfterViewInit, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { AbstractControl, FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { Subscription } from 'rxjs';
import { Role } from 'src/app/models/role/role';
import { LoginRequest } from 'src/app/models/user/login/login-request';
import { RegisterRequest } from 'src/app/models/user/register/register-request';
import { AccountService } from 'src/app/services/account.service';
import { AuthService } from 'src/app/services/auth.service';
import { RoleService } from 'src/app/services/role.service';


@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit, OnDestroy {
  signUpForm!: FormGroup;
  loginForm!: FormGroup;
  roles: Role[] = [];
  registerRequest!: RegisterRequest;
  loginRequest!: LoginRequest;
  userName?: string;
  currentUserSub?: Subscription;
  role?: string;
  activateAdminPanel?: boolean;
  activateResource?: boolean;
  @ViewChild('signUpCloseBtn') signUpCloseBtn?: ElementRef;
  @ViewChild('loginCloseBtn') loginCloseBtn?: ElementRef;

  constructor(
    private accountService: AccountService,
    protected authService: AuthService,
    private roleService: RoleService,
    private spinnerService: NgxSpinnerService,
    private messageService: MessageService) {

      this.currentUserSub = this.accountService.currentUser.subscribe({
        next: (user) => {
          this.userName = user?.userName;

          this.role = user?.role;
          this.activateAdminPanel= this.authService.roleMatch(['Admin']);
          this.activateResource= this.authService.roleMatch(['Admin','Employee']);
        }

      });
      this.userName= localStorage.getItem('userName') as string;

  }


  ngOnInit(): void {

    this.getRoles();
    this.createSignUpForm();
    this.createLoginForm();
  }

  ngOnDestroy(): void {
    this.currentUserSub?.unsubscribe();
  }

  getRoles() {
    this.roleService.getCurrentUserRoles().subscribe({
      next: (roles) => {
        this.roles = roles;
      },
      error: (error) => {
        this.roles = [];
        if (error?.error?.message) {
          this.messageService.add({severity:'error', summary:'Error Retriving data', detail: error.error.message})
        } else {
          this.messageService.add({severity:'error', detail: 'some thing went wrong!'});

        }
      }
    });
  }


  onSignUpSubmit() {
    if (this.signUpForm.valid) {
      this.registerRequest = {
        name: this.signUpForm.value.name,
        role: this.signUpForm.value.role,
        email: this.signUpForm.value.email,
        password: this.signUpForm.value.password
      };
      this.accountService.register(this.registerRequest).subscribe({
        next: () => {
          this.messageService.add({severity:'success', detail: 'Registerd successfully, please wait for admin approval to login!'});
          this.signUpCloseBtn?.nativeElement.click();
        },
        error: (error) => {
          if (error?.error?.message) {
            this.messageService.add({severity:'error', detail: error.error.message});
          } else {
            this.messageService.add({severity:'error', detail: 'some thing went wrong!'});

          }
        }
      })
    }
  }

  onLoginSumbit() {
    if (this.loginForm.valid) {
      this.loginRequest = {
        ...this.loginForm.value
      };
      this.spinnerService.show();
      this.accountService.login(this.loginRequest).subscribe({
        next: (response) => {
            this.spinnerService.hide();
          this.userName= response.name;
          this.messageService.add({severity:'success', detail: 'User ' + response.name +'Logged in successfully'});
          this.loginCloseBtn?.nativeElement.click();
        },
        error: (error) => {
            this.spinnerService.hide();

          if (error.error?.message) {
            this.messageService.add({severity:'error', detail: error.error.message});
          }

          if (error.status === 401) {
            this.messageService.add({severity:'error', detail: "Invalid credentials!"})
          }
        }
      });
    }
  }

  onLogoutClicked() {
    this.activateAdminPanel= false;
    this.activateResource= false;
    this.accountService.logout();
    this.messageService.add({severity:'success', detail: 'Logged out successfully'})
  }

  private createSignUpForm() {
    this.signUpForm = new FormGroup({
      name: new FormControl(null, [Validators.required, Validators.maxLength(60)]),
      password: new FormControl<string>('', [Validators.required, Validators.minLength(6), Validators.maxLength(24)]),
      confirmPassword: new FormControl<string>('', [Validators.required]),
      email: new FormControl<string>('', [Validators.required, Validators.email]),
      role: new FormControl<Role | null>(null, [Validators.required])
    }, { validators: this.passwordConfirming });
  }

  private createLoginForm() {
    this.loginForm = new FormGroup({
      email: new FormControl<string>('', [Validators.required, Validators.email]),
      password: new FormControl<string>('', [Validators.required, Validators.minLength(6), Validators.maxLength(24)])
    });
  }


  isUserLoggedIn(): boolean {
    return this.accountService.isLoggedIn();

  }

  private passwordConfirming(c: AbstractControl): { mismatch: boolean } | null {
    if (c.get('password')?.value !== c.get('confirmPassword')?.value) {
      return {mismatch: true};
    }
    return null;
  }
}
