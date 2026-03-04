import { Component, Input, OnInit } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { AccountService } from 'src/app/services/account.service';
import { AuthService } from 'src/app/services/auth.service';
import { RoleService } from 'src/app/services/role.service';
import {DropdownModule} from 'primeng/dropdown';

@Component({
  selector: 'app-all-account',
  templateUrl: './all-account.component.html',
  styleUrls: ['./all-account.component.scss'],
  styles: [`
  :host ::ng-deep .p-cell-editing {
      padding-top: 0 !important;
      padding-bottom: 0 !important;
  }
`]
})
export class AllAccountComponent implements OnInit{

  @Input('data')data: any[];
  @Input('cols')cols: any[];

  dataBackups:any[];
  roles: any[];

  constructor(
    private accountService: AccountService,
    protected authService: AuthService,
    private roleService: RoleService,
    private spinnerService: NgxSpinnerService,
    private messageService: MessageService
  ){

  }
  ngOnInit(): void {
    this.getRoles();
    this.dataBackups=this.data;
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

  clonedAccount:any;
  onRowEditInit(account: any) {
    if(!this.dataBackups || this.data.length != this.dataBackups.length){
      this.dataBackups=this.data;
    }
    this.clonedAccount = {...account};
    let role= this.roles.find(x=>(x.name as string).toLowerCase() === (account.role as string).toLowerCase())
    account.role = role.name;
}

onRowEditSave(account: any, index: number) {
    if ((this.dataBackups[index].role as string).toLowerCase() !== (account.role as string).toLowerCase()) {
      let obj={
          newRole: account.role
      }

      this.spinnerService.show();
    this.accountService.updateUsersRole(account.id,obj).subscribe({
      next: (roles) => {
        this.spinnerService.hide();

        // delete this.clonedAccount[account.id];
        this.dataBackups[index] = this.clonedAccount;

        this.messageService.add({severity:'success', detail: 'user role updated successfully!'});
      },
      error: (error) => {
        this.spinnerService.hide();

        this.roles = [];
        if (error?.error?.message) {
          this.messageService.add({severity:'error', summary:'Error Retriving data', detail: error?.error?.message || 'some thing went wrong'})
        } else {
          this.messageService.add({severity:'error', detail: 'some thing went wrong!'});

        }
      }
    });

    }
    else {
      this.messageService.add({severity:'error', summary: 'Error', detail:'Same role'});
    }
}

onRowEditCancel(account: any, index: number) {
    this.dataBackups[index] = this.clonedAccount;
    delete this.clonedAccount;
}

}
