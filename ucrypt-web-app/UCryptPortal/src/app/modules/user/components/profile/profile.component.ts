import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { AccountService } from 'src/app/services/account.service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {

  currentUser: any;
  keys: any[];
  cols: any[];
  constructor(
    private _accountService:AccountService,
    private spinnerService: NgxSpinnerService,
    private messageService: MessageService    ) {}

  ngOnInit(): void {
    this.getCols();
    this.getCurrentUser();
    this.getKeys();
  }

  getCols(){
    this.cols = [
      { field: "id", header: "Id", hidden: false },
      { field: "value", header: "Key", hidden: false },

    ];
  }
  getCurrentUser(){
    this.spinnerService.show();
    this._accountService.getCurrentUser().subscribe({
      next: (user) => {
        this.spinnerService.hide();
        this.currentUser= user;
      },
      error: (error) => {
        this.spinnerService.hide();

        if (error?.error?.message) {
          this.messageService.add({severity:'error', summary:'Error Retriving data', detail: error.error.message})
        } else {
          this.messageService.add({severity:'error', detail: 'some thing went wrong!'});

        }
      }
    })
  }

  getKeys(){
    this.spinnerService.show();
    this._accountService.getKeys().subscribe({
      next: (keys) => {
        this.spinnerService.hide();
        this.keys= keys;
      },
      error: (error) => {
        this.spinnerService.hide();

        if (error?.error?.message) {
          this.messageService.add({severity:'error', summary:'Error Retriving data', detail: error.error.message})
        } else {
          this.messageService.add({severity:'error', detail: 'some thing went wrong!'});

        }
      }
    })
  }

}
