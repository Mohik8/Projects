import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { JwtHelperService } from '@auth0/angular-jwt';
import { ReplaySubject } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { LoginRequest } from '../models/user/login/login-request';
import { LoginResponse } from '../models/user/login/login-response';
import { RegisterRequest } from '../models/user/register/register-request';
import { User } from '../models/user/user';

@Injectable({
  providedIn: 'root'
})
export class AccountService {

  baseUrl = environment.apiUrl + 'users';
  private currentUserSource = new ReplaySubject<User | null>();
  currentUser = this.currentUserSource.asObservable();
  private jwtHelper = new JwtHelperService();
  baseEmployeeUrl = environment.apiUrl + 'employees';


  constructor(private http: HttpClient, private router: Router) { }

  login(model: LoginRequest) {
    return this.http.put<LoginResponse>(this.baseUrl + '/login', model).pipe(
      map( (response: LoginResponse) => {
        if (response) {
          this.setCurrentUser(response);
        }
        return response;
      })
    );
  }

  autoLogin(){
    let token= localStorage.getItem('token');
    let user = localStorage.getItem('userName')!;
    let role = sessionStorage.getItem('role')!;
    if(token && !this.jwtHelper._isTokenExpired(token)){
      let newUser: User ={
        userName: user ,
        role: role
      }
      this.currentUserSource.next(newUser);
    } else {
      this.logout();
    }
  }
  private setCurrentUser(loginResponse: LoginResponse) {
    // const user: User = {userName: loginResponse.name,role:loginResponse.role.name};
    const user: User = {userName: loginResponse.name,role:this.jwtHelper.decodeToken(loginResponse.accessToken)['role']};
    localStorage.setItem('token', loginResponse.accessToken);
    localStorage.setItem('userName', loginResponse.name);
    // localStorage.setItem('role', loginResponse.role.name);
    sessionStorage.setItem('role', this.jwtHelper.decodeToken(loginResponse.accessToken)['role']);
    this.currentUserSource.next(user);
  }



  register(model: RegisterRequest) {
    return this.http.post(this.baseUrl + '/register', model);
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userName');
    sessionStorage.removeItem('role');
    this.currentUserSource.next(null);
    this.router.navigate(['/index']);
  }

  isLoggedIn(): boolean {
    const token = localStorage.getItem('token');
    if (token) {
      return !this.jwtHelper.isTokenExpired(token);
    }
    // this.router.navigate(['/index']);
    return false;
  }


  saveKey(model: any) {
    return this.http.post<any>(this.baseUrl + '/current/encryption-keys', model);
  }

  getKeys() {
    return this.http.get<any[]>(this.baseUrl + '/current/encryption-keys');
  }

  getCurrentUser() {
    return this.http.get<any>(this.baseUrl + '/current');
  }

  getUsers() {
    return this.http.get<any[]>(this.baseUrl);
  }

  activateAccount(id: any) {
    return this.http.put<any>(this.baseUrl + `/${id}/active`,null);
  }

  deactivateAccount(id: any) {
    return this.http.delete<any>(this.baseUrl + `/${id}/active`);
  }

  updateUsersRole(id: any,obj: any) {
    return this.http.put<any>(this.baseUrl + `/${id}/role`,obj);
  }

  getEmployees() {
    return this.http.get<any[]>(this.baseEmployeeUrl);

  }


}
