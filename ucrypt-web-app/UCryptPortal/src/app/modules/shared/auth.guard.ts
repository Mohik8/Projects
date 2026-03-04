import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, CanActivateChild, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from 'src/app/services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate ,CanActivateChild{
  constructor(
    private _authService:AuthService,
    private router:Router,

  ){
  }

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
      // if(this._authService.getToken() || this._authService.getToken() !=='' ){
      //   const role = route.data['role'] as Array<string>;

      //   if(role){
      //     const match = this._authService.roleMatch(role);
      //     if(match){
      //       return true;
      //     } else {
      //       this.router.navigate(['/index']);
      //       return false;
      //     }
      //   }
      // }
      // this.router.navigate(['/index']);
      // return false;
      return true;
  }

  canActivateChild(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
      return true;
  }

}
