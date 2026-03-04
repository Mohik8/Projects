import { Component, ElementRef, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { AccountService } from 'src/app/services/account.service';
import { AuthService } from 'src/app/services/auth.service';
import { RoleService } from 'src/app/services/role.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
})
export class HomeComponent {
  isOpen: boolean = false;
  hide: boolean = false;
  @ViewChild('MyModal', { static: true }) MyModal: ElementRef;
  constructor(
    private accountService: AccountService,
    private authService: AuthService,
    private router: Router,

    private roleService: RoleService,
    private spinnerService: NgxSpinnerService,
    private messageService: MessageService
  ) {}
  goToEncryption() {
    if (this.isUserLoggedIn()) {
      this.router.navigate(['/encryption']);
      this.hide = true;
    } else {
      this.isOpen = true;
      this.hide = false;

      this.MyModal.nativeElement.click();
    }
  }

  goToDecryption() {
    if (this.isUserLoggedIn()) {
      this.router.navigate(['/decryption']);
      this.hide = true;
    } else {
      this.isOpen = true;
      this.hide = false;

      this.MyModal.nativeElement.click();
    }
  }
  isUserLoggedIn(): boolean {
    return this.accountService.isLoggedIn();
  }
}
