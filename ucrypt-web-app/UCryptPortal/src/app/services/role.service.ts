import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map } from 'rxjs';
import { Role } from 'src/app/models/role/role';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class RoleService {

  baseUrl = environment.apiUrl + 'roles/';

  constructor(private http: HttpClient) { }

  getCurrentUserRoles() {
    return this.http.get<Role[]>(this.baseUrl + 'new-users').pipe(
      map(res=>{
        let adminFound = res.findIndex(r=>r.name.toLowerCase() === 'admin');
        if(adminFound>=0){
          res.splice(adminFound,1);
        }
        return res;
      })
    )

  }



}
