import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-contact',
  templateUrl: './contact.component.html',
  styleUrls: ['./contact.component.scss']
})
export class ContactComponent implements OnInit{

  form:FormGroup;
  submitted:boolean=false;
  phonePattern= '^[0-9]{10}$';

  constructor(
    private _fb:FormBuilder,
    private spinnerService: NgxSpinnerService,
    private messageService: MessageService
  ){

  }
  ngOnInit(): void {
    this.createForm();
  }


  createForm(){
    this.form= this._fb.group({
      name:['',Validators.required],
      phone:['',Validators.required],
      email:['',[Validators.required, Validators.email]],
      subject:['',Validators.required],
      message:['',Validators.required],
    })
  }


  onSubmit(){
    debugger
    this.submitted= true;
    if(this.form.valid){
      // alert("Thank you for contacting us. One of our customer representatives will get back to you shortly.")
      this.spinnerService.show();
      setTimeout(() => {
        this.spinnerService.hide();
        this.messageService.add({severity:'success', detail: 'Thank you for contacting us. One of our customer representatives will get back to you shortly."'});
      }, 1000);
    }

  }

}
