import { Component, OnInit } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { AccountService } from 'src/app/services/account.service';

@Component({
  selector: 'app-company',
  templateUrl: './company.component.html',
  styleUrls: ['./company.component.scss']
})
export class CompanyComponent implements OnInit {
  emps:any[]=[];


  constructor(
    private spinnerService: NgxSpinnerService,
    private messageService: MessageService,
    private _accountService:AccountService
  ){

  }

  ngOnInit(): void {
      this.getEmployees();
  }

  getEmployees(){
    this.spinnerService.show();
    this._accountService.getEmployees().subscribe({
      next: (algos) => {
        this.spinnerService.hide();
        this.emps = algos;
      },
      error: (error) => {
        this.spinnerService.hide();
        this.emps = [];
        if (error?.error?.message) {
          this.messageService.add({severity:'error', summary:'Error Retriving data', detail: error.error.message})
        } else {
          this.messageService.add({severity:'error', detail: 'some thing went wrong!'});

        }
      }
    });
  }

}
