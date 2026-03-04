import { Component } from '@angular/core';

@Component({
  selector: 'app-admin-layout',
  templateUrl: './admin-layout.component.html',
  styleUrls: ['./admin-layout.component.scss']
})
export class AdminLayoutComponent {

  newAccountsCount: number =0;
  constructor(){

  }

  getCount(count:number){

    if(count){
      this.newAccountsCount= count;
    }
  }
}
