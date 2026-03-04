import { Component, OnInit } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { Role } from 'src/app/models/role/role';
import { RoleService } from 'src/app/services/role.service';

@Component({
  selector: 'app-roles',
  templateUrl: './roles.component.html',
  styleUrls: ['./roles.component.scss']
})
export class RolesComponent implements OnInit{
  roles: Role[] = [];
  Cols: any[] = [];

  constructor(
    private roleService: RoleService,
    private spinnerService: NgxSpinnerService,
    private messageService: MessageService
  ){

  }

  ngOnInit(): void {
    this.getCols();
    this.getRoles();
  }
  getRoles() {

    this.spinnerService.show();
    this.roleService.getCurrentUserRoles().subscribe({
      next: (roles) => {
        this.spinnerService.hide();

        this.roles = roles;
      },
      error: (error) => {
        this.spinnerService.hide();

        this.roles = [];
        if (error?.error?.message) {
          this.messageService.add({severity:'error', summary:'Error Retriving data', detail: error.error.message})
        } else {
          this.messageService.add({severity:'error', detail: 'some thing went wrong!'});

        }
      }
    });
  }

  getCols(){
    this.Cols = [
      { field: "id", header: "Id", hidden: false },
      {
        field: "displayName",
        header: "Name",
        hidden: false,
      },

    ];
  }
}
