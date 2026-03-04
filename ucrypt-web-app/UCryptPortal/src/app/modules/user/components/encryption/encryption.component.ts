import { Component, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { FileUpload } from 'primeng/fileupload';
import { forkJoin } from 'rxjs';
import { EncryptionAlgorithm } from 'src/app/models/encryptionAlgorithm/encryption-algorithm';
import { AccountService } from 'src/app/services/account.service';
import { EncryptionAlgorithmService } from 'src/app/services/encryption-algorithm.service';
import { EncryptionService } from 'src/app/services/encryption.service';

@Component({
  selector: 'app-encryption',
  templateUrl: './encryption.component.html',
  styleUrls: ['./encryption.component.scss'],
})
export class EncryptionComponent {

  @ViewChild('fileUpload') fileUpload: FileUpload;

  form: FormGroup;
  fileForm: FormGroup;
  algorithms:EncryptionAlgorithm[];
  submitted: boolean = false;
  fileSubmitted: boolean = false;
  fileEncryptionObject: FileEncryption;
  uploadedFiles: any[] = []
  showFileUpload: boolean= true;
  showFilePendingForm: boolean= false;
  showFileFinishedDetails: boolean= false;

  constructor(
    private fb:FormBuilder,
    private _encryptionService:EncryptionService,
    private _accountService:AccountService,
    private spinnerService: NgxSpinnerService,
    private _encryptionAlgorithmService:EncryptionAlgorithmService,
    private messageService: MessageService
  ){}

  ngOnInit(): void {
    this.getAlgorithms();
    this.createForm();
    this.createFileForm();
  }

  createFileForm(){
    this.fileForm= this.fb.group({
      file:['',Validators.required],
      encryptionTechnique:['',Validators.required],
      encryptionKey:['',Validators.required],
      encryptedText:['']
    })
  }
  copykey(element: HTMLTextAreaElement) {
    if (!element) return;

    const value = element.value;

    if (!value) {
      this.messageService.add({severity:'warn', detail: 'Nothing to copy!'});
      return;
    }

    if (navigator.clipboard) {
      navigator.clipboard.writeText(value).then(() => {
        this.messageService.add({severity:'success', detail: 'Copied to clipboard!'});
      }).catch(() => {
        this.messageService.add({severity:'error', detail: 'Copy failed!'});
      });
    } else {
      element.select();
      try {
        const successful = document.execCommand('copy');
        if (successful) {
          this.messageService.add({severity:'success', detail: 'Copied to clipboard!'});
        } else {
          this.messageService.add({severity:'error', detail: 'Copy failed!'});
        }
      } catch {
        this.messageService.add({severity:'error', detail: 'Copy failed!'});
      }
      window.getSelection()?.removeAllRanges();
    }
  }

  createForm(){
    this.form= this.fb.group({
      textToEncrypt:[null,Validators.required],
      encryptionTechnique:['',Validators.required],
      encryptionKey:['',Validators.required],
      encryptedText:['']
    })
  }

  getAlgorithms() {
    this.spinnerService.show();
    this._encryptionAlgorithmService.getEncryptionAlgo().subscribe({
      next: (algos) => {
        this.spinnerService.hide();
        this.algorithms = algos;
      },
      error: (error) => {
        this.spinnerService.hide();
        this.algorithms = [];
        if (error?.error?.message) {
          this.messageService.add({severity:'error', summary:'Error Retriving data', detail: error?.error?.message || 'some thing went wrong'})
        } else {
          this.messageService.add({severity:'error', detail: 'some thing went wrong!'});

        }
      }
    });
  }

  generateKey( isFile?:boolean){
    if(!isFile){
      if( this.form.get('encryptionTechnique')?.value ==='' || !this.form.get('encryptionTechnique')?.value){
        this.messageService.add({severity:'error', summary:'Error Empty data', detail: 'encryptionTechnique field is not selected '})
        return;
      }
    } else{
      if(isFile&& this.fileForm.get('encryptionTechnique')?.value ==='' || !this.fileForm.get('encryptionTechnique')?.value){
        this.messageService.add({severity:'error', summary:'Error Empty data', detail: 'encryptionTechnique field is not selected '})
        return;
      }
    }
    const encTeq = {encryptionAlgorithm: (isFile)? this.fileForm.get('encryptionTechnique')?.value: this.form.get('encryptionTechnique')?.value};
    this.spinnerService.show();
    this._encryptionAlgorithmService.generateKey(encTeq).subscribe({
      next: (response) => {
        this.spinnerService.hide();
        if(isFile){
          this.fileForm.get('encryptionKey')?.setValue(response.key);
        }else {
          this.form.get('encryptionKey')?.setValue(response.key);
        }
    },
    error: (error) => {
      this.spinnerService.hide();
      if (error.error?.message) {
        this.messageService.add({severity:'error', detail: error?.error?.message || 'some thing went wrong'});
      }

      if (error.status === 401) {
        this.messageService.add({severity:'error', detail: "Invalid credentials!"})
      }
    }
    })
  }

  saveKey(isFile?:boolean){
    if(isFile){
      if( this.fileForm.get('encryptionKey')?.invalid || this.fileForm.get('encryptionTechnique')?.invalid){
        this.fileSubmitted= true;
        this.messageService.add({severity:'error', detail: 'please fill the required fields'});
        return;
      }
    }else {
      if( this.form.get('encryptionKey')?.invalid || this.form.get('encryptionTechnique')?.invalid){
        this.submitted= true;
        this.messageService.add({severity:'error', detail: 'please fill the required fields'});
        return;
      }
    }

    let savedKeyModel = {
      value: (isFile)? this.fileForm.get('encryptionKey')?.value: this.form.get('encryptionKey')?.value,
      encryptionAlgorithm: (isFile)? this.fileForm.get('encryptionTechnique')?.value :this.form.get('encryptionTechnique')?.value
    }
    this.spinnerService.show();
    this._accountService.saveKey(savedKeyModel).subscribe({
      next: (response) => {
        this.spinnerService.hide();
        this.messageService.add({severity:'success', detail: 'Key is Saved Successfully'});
      },
      error: (error) => {
        this.spinnerService.hide();
        if (error.error?.message) {
          this.messageService.add({severity:'error', detail: error?.error?.message || 'some thing went wrong'});
        }

        if (error.status === 401) {
          this.messageService.add({severity:'error', detail: "Invalid credentials!"})
        }
      }
    })
  }

  onUpload(event: any){
    for(let file of event.files) {
      this.fileForm.patchValue({ file: file });
      this.fileForm.get('file')!.updateValueAndValidity();
      this.uploadedFiles.push(file);
      this.readAndUploadFile(event.files[0]);
    }
  }

  mapTextModel(){
    const textModel= {
      key:this.form.value.encryptionKey,
      text:this.form.value.textToEncrypt,
      encryptionAlgorithm:this.form.value.encryptionTechnique,
    };
    return textModel;
  }

  encrypt(isFile?: boolean){
    if(isFile){
      this.fileSubmitted = true;
      if(this.fileForm.valid){
        this.fileEncryptionObject.key= this.fileForm.value.encryptionKey;
        this.fileEncryptionObject.encryptionAlgorithm= this.fileForm.value.encryptionTechnique;
        this.encryptFile(this.fileEncryptionObject);
      }
    }else{
      this.submitted = true;
      if(this.form.valid){
      this.encryptText(this.mapTextModel());
      }
    }
  }

  downloadFile(data: any) {
    const blob = new Blob([data], { type: data.type });
    const url= window.URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = this.fileEncryptionObject.fileName;
    link.click();
    // window.open(url);
  }

  encryptFile(model: any){
    this.spinnerService.show();
    this._encryptionService.encryptFile(model).subscribe({
      next: (response) => {
        this.spinnerService.hide();
          this.downloadFile(response);
          this.fileSubmitted = false;
          this.showFilePendingForm= false;
          this.showFileUpload= false;
          this.showFileFinishedDetails= true;
          this.fileUpload.clear()
      this.messageService.add({severity:'success', detail: 'data encrypted successfully'});
    },
    error: async (error) => {
        this.spinnerService.hide();
      if (error.error?.message) {
        this.messageService.add({severity:'error', detail: error?.error?.message || 'some thing went wrong'});
      }
      if (error?.status !== 401 && !error.error?.message) {
        const message = JSON.parse(await error.error.text()).message;

        this.messageService.add({severity:'error', detail: message});
      }

      if (error.status === 401) {
        this.messageService.add({severity:'error', detail: "Invalid credentials!"})
      }
    }

    })
  }

  encryptText(model: any){
    this.spinnerService.show();
    this._encryptionService.encryptText(model).subscribe({
      next: (response) => {
        this.spinnerService.hide();
        this.submitted = false;
        this.form.reset();
        this.form.get('encryptedText')?.setValue(response.encryptedText);
      this.messageService.add({severity:'success', detail: 'data encrypted successfully '});
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

  backToUpload(){
    this.showFilePendingForm= false;
    this.showFileFinishedDetails= false;
    this.showFileUpload= true;
  }

  private readAndUploadFile(theFile: any) {
    (this.fileEncryptionObject as any)={};
    let reader = new FileReader();

    reader.onload = () => {
        let fileInBytes = this.convertDataURIToBinary(reader.result);
        var array = Array.from(fileInBytes)
        this.fileEncryptionObject.fileName=theFile.name;
        this.fileEncryptionObject.fileType=theFile.type;
        this.fileEncryptionObject.size=theFile.size;
        this.fileEncryptionObject.file= array;
        this.fileEncryptionObject.key= this.form.value.encryptionKey;
        this.fileEncryptionObject.encryptionAlgorithm= this.form.value.encryptionTechnique;

        this.showFileUpload= false;
        this.showFilePendingForm= true;
        this.showFileFinishedDetails= false;
    }
    reader.readAsDataURL(theFile);
  }

  private convertDataURIToBinary(dataURI: any) {
    var base64Index = dataURI.indexOf(';base64,') + ';base64,'.length;
    var base64 = dataURI.substring(base64Index);
    var raw = window.atob(base64);
    var rawLength = raw.length;
    var array = new Uint8Array(new ArrayBuffer(rawLength));
    for(let i = 0; i < rawLength; i++) {
      array[i] = raw.charCodeAt(i);
    }
    return array;
  }

}

export interface FileEncryption{
  key: string;
  file: number[];
  size: number;
  fileName: string;
  fileType: string;
  encryptionAlgorithm: string;
}
