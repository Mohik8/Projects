import { Component, OnInit, ViewChild } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { FileUpload } from 'primeng/fileupload';
import { FileService } from 'src/app/services/file.service';

@Component({
  selector: 'app-resources',
  templateUrl: './resources.component.html',
  styleUrls: ['./resources.component.scss']
})
export class ResourcesComponent implements OnInit {
  fileToUpload: number[];
  downloadedFileName: string = '';
  filesList: any[];
  @ViewChild('fileUpload') fileUpload: FileUpload;

  constructor(
    private spinnerService: NgxSpinnerService,
    private _fileService: FileService,
    private messageService: MessageService
  ) { }

  ngOnInit(): void {
    this.getFilesList();
  }

  onUpload(event: any) {
    this.spinnerService.show();
    this._fileService.createFile(event.files[0]).subscribe({
      next: (response) => {
        this.spinnerService.hide();
        this.getFilesList();
        this.fileUpload.clear();
        this.messageService.add({ severity: 'success', detail: 'file is uploaded successfully' });
      },
      error: (error) => {
        this.spinnerService.hide();

        if (error.error?.message) {
          this.messageService.add({ severity: 'error', detail: error.error.message });
        }

        if (error.status === 401) {
          this.messageService.add({ severity: 'error', detail: "Invalid credentials!" });
        }
      }
    });
  }

  getFilesList() {
    this.spinnerService.show();
    this._fileService.getFiles().subscribe({
      next: (response) => {
        this.spinnerService.hide();
        this.filesList = response;
      },
      error: (error) => {
        this.spinnerService.hide();

        if (error.error?.message) {
          this.messageService.add({ severity: 'error', detail: error.error.message });
        }

        if (error.status === 401) {
          this.messageService.add({ severity: 'error', detail: "Invalid credentials!" });
        }
      }
    });
  }

  downloadFileHelper(data: any, filename: string) {
    const blob = new Blob([data], { type: data.type });
    const url = window.URL.createObjectURL(blob);
    var link = document.createElement('a');
    setTimeout(() => {
      link.href = url;
      link.download = this.downloadedFileName;
      link.click();
    }, 0);
  }

  downloadFile(file: any) {
    if (file.type === 'application/octet-stream' && !(file.name as string).includes('.')) {
      this.downloadedFileName = file.name + '.txt'
    } else {
      this.downloadedFileName = file.name;
    }
    this.spinnerService.show();
    this._fileService.downloadFile(file.path).subscribe({
      next: (response) => {
        this.downloadFileHelper(response, file.name as string);
        this.spinnerService.hide();
      },
      error: (error) => {
        this.spinnerService.hide();

        if (error.error?.message) {
          this.messageService.add({ severity: 'error', detail: error.error.message });
        }

        if (error.status === 401) {
          this.messageService.add({ severity: 'error', detail: "Invalid credentials!" });
        }
      }
    });
  }

  deleteFile(file: any) {
    this.spinnerService.show();
    this._fileService.deleteFile(file.path).subscribe({
      next: () => {
        this.spinnerService.hide();
        this.getFilesList();
        this.messageService.add({ severity: 'success', detail: 'File deleted successfully' });
      },
      error: (error) => {
        this.spinnerService.hide();

        if (error.error?.message) {
          this.messageService.add({ severity: 'error', detail: error.error.message });
        }

        if (error.status === 401) {
          this.messageService.add({ severity: 'error', detail: "Invalid credentials!" });
        }
      }
    });
  }
}
