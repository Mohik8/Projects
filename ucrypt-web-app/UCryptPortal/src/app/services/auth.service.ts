import { Injectable } from '@angular/core';
import { Subscription } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  currentUserSub?: Subscription;
  myrole: string = '';
  constructor(
    private accountService: AccountService,

  ) {
    this.currentUserSub = this.accountService.currentUser.subscribe({
      next: (user) => {
        this.myrole = user?.role!;

      }

    });
   }

  getRole(){
    return sessionStorage.getItem('role')!;
  }

  getToken(){
    return localStorage.getItem('token');
  }

  roleMatch(allowedRoles: string[]):boolean{
    let isMatch: boolean= false;
    let currentRole = this.getRole();

    if(currentRole!= '' && currentRole){
      for(let i=0; i<allowedRoles.length;i++){
        if(currentRole.toLocaleLowerCase() === allowedRoles[i].toLocaleLowerCase()){
          isMatch= true;
          return isMatch;
        }
      }
    }
    return isMatch;
  }


}


