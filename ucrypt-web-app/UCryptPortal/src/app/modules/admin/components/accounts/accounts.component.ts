import { Component, EventEmitter, Output } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { AccountService } from 'src/app/services/account.service';

@Component({
  selector: 'app-accounts',
  templateUrl: './accounts.component.html',
  styleUrls: ['./accounts.component.scss'],
})
export class AccountsComponent {

  @Output()newAccountsCount = new EventEmitter<number>();

  Cols: any[]= [];
  allUsers: any[]= [];
  staff: any[]= [];
  newAccount: any[]= [];
  userAccount: any[]= [];
  allUsersCount: number= 0;
  staffCount:  number= 0;
  newAccountCount:  number= 0;
  userAccountCount:  number= 0;
  constructor(
    private _accountService:AccountService,
    private spinnerService: NgxSpinnerService,
    private messageService: MessageService

  ){

  }
  ngOnInit(){
    this.getCols();
    this.getAllUsers();
  }


  getCols(){
    this.Cols = [
      { field: "id", header: "Id", hidden: true },
      { field: "email", header: "Email", hidden: false },
      {
        field: "name",
        header: "Name",
        hidden: false,
      },
      {
        field: "role",
        header: "Role",
        hidden: false,
      },
      {
        field: "status",
        header: "Status",
        hidden: false,
      },

    ];
  }

  getAllUsers(){
    this.spinnerService.show();
    this._accountService.getUsers().subscribe({
      next: (users) => {
        try{
          let mappedUsers= users.map(function(user) {
            return {
              role: user.role.name,
              id: user.id,
              email: user.email,
              name: user.name,
              status: user.status,
            }
          }
          );
          this.allUsers = mappedUsers
          this.staff = mappedUsers.filter(x=>(x.status as string).toLowerCase() === 'active' && (x.role as string ).toLowerCase() === 'employee');
          this.newAccount = mappedUsers.filter(x=>(x.status as string).toLowerCase() === 'created' );;
          this.userAccount = mappedUsers.filter(x=>(x.status as string).toLowerCase() === 'active' && (x.role as string ).toLowerCase() === 'user');
          this.allUsersCount= this.allUsers.length;
          this.staffCount= this.staff.length;
          this.newAccountCount= this.newAccount.length;
          this.userAccountCount= this.userAccount.length;
          this.spinnerService.hide();

          this.newAccountsCount.emit(this.newAccountCount)
        } catch(e){
          this.spinnerService.hide();
        }

      },
      error: (error) => {
        this.spinnerService.hide();
        this.allUsers = [];
        this.staff = [];
        this.newAccount = [];
        this.userAccount = [];
        this.allUsersCount= 0;
        this.staffCount= 0;
        this.newAccountCount= 0;
        this.userAccountCount= 0;
        if (error?.error?.message) {
          this.messageService.add({severity:'error', summary:'Error Retriving data', detail: error.error.message})
        }
        else {
          this.messageService.add({severity:'error', detail: 'some thing went wrong!'});

        }
      }
    })
  }

  activateAccount(event: boolean){
    if(event){
      this.allUsers = [];
      this.staff = [];
      this.newAccount = [];
      this.userAccount = [];
      this.getAllUsers();
    }
  }
  deactivateAccount(event: boolean){
    if(event){
      this.allUsers = [];
      this.staff = [];
      this.newAccount = [];
      this.userAccount = [];
      this.getAllUsers();
    }
  }
}

