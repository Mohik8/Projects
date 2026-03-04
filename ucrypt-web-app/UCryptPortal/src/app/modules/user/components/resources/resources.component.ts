import { Component, OnInit } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { FileService } from 'src/app/services/file.service';

@Component({
  selector: 'app-resources',
  templateUrl: './resources.component.html',
  styleUrls: ['./resources.component.scss']
})
export class ResourcesComponent implements OnInit{
  filesList:any[];
  downloadedFileName: string='';

  constructor(
    private spinnerService: NgxSpinnerService,
    private _fileService:FileService,
    private messageService: MessageService

  ){

  }

  ngOnInit(): void {
    this.getFilesList();
  }

  getFilesList(){
    this.spinnerService.show();

    this._fileService.getFiles().subscribe({
      next: (response) => {
        this.spinnerService.hide();
        this.filesList = response;
    },
    error: (error) => {
        this.spinnerService.hide();

      if (error.error?.message) {
        this.messageService.add({severity:'error', detail: error.error.message});
      }

      if (error.status === 401) {
        this.messageService.add({severity:'error', detail: "Invalid credentials!"})
      }
    }

    })

  }


  downloadFileHelper(data: any,filename: string) {
    const blob = new Blob([data], { type: data.type });
    const url= window.URL.createObjectURL(blob);
    var link = document.createElement('a');
    setTimeout(() => {
      link.href = url;
      link.download = this.downloadedFileName;
      link.click();
    }, 0);
  }

  downloadFile(file: any){
    if(file.contentType === 'application/octet-stream'&& !(file.name as string).includes('.')){
      this.downloadedFileName = file.name+ '.txt'
    } else {
      this.downloadedFileName = file.name;
    }    this.spinnerService.show();
    this._fileService.downloadFile(file.path).subscribe({
      next: (response) => {
        this.downloadFileHelper(response,file.name as string);
        this.spinnerService.hide();
    },
    error: (error) => {
        this.spinnerService.hide();

      if (error.error?.message) {
        this.messageService.add({severity:'error', detail: error.error.message});
      }

      if (error.status === 401) {
        this.messageService.add({severity:'error', detail: "Invalid credentials!"})
      }
    }

    })

  }
}
