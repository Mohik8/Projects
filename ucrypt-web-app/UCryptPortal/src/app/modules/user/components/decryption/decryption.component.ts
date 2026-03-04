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
import { FileEncryption } from '../encryption/encryption.component';

@Component({
  selector: 'app-decryption',
  templateUrl: './decryption.component.html',
  styleUrls: ['./decryption.component.scss']
})
export class DecryptionComponent {

  @ViewChild('fileUpload') fileUpload: FileUpload;

  form: FormGroup;
  fileForm: FormGroup;
  algorithms:EncryptionAlgorithm[];
  fileEncryptionObject: FileDecryption;
  keys:any[]=[];
  uploadedFiles: any[] = []
  submitted: boolean= false;
  fileSubmitted: boolean= false;
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
    this.getUserKeys();
    this.createForm();
    this.createFileForm();
  }

  createFileForm(){
    this.fileForm= this.fb.group({
      file:['',Validators.required],
      encryptionTechnique:['',Validators.required],
      encryptionKey:[''],
      encryptionKeySelected:['',Validators.required],
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
      textToDecrypt:[null,Validators.required],
      encryptionTechnique:['',Validators.required],
      encryptionKey:[''],
      encryptionKeySelected:['',Validators.required],
      decryptedText:['']
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
          this.messageService.add({severity:'error', summary:'Error Retriving data', detail: error.error.message})
        } else {
          this.messageService.add({severity:'error', detail: 'some thing went wrong!'});

        }
      }
    });
  }

  getUserKeys() {
    this.spinnerService.show();
    this._accountService.getKeys().subscribe({
      next: (res) => {
        this.spinnerService.hide();
        this.keys = res;
      },
      error: (error) => {
        this.spinnerService.hide();
        this.keys = [];
        if (error?.error?.message) {
          this.messageService.add({severity:'error', summary:'Error Retriving data', detail: error.error.message})
        } else {
          this.messageService.add({severity:'error', detail: 'some thing went wrong!'});

        }
      }
    });
  }


  onUpload(event: any){
    for(let file of event.files) {
      this.fileForm.patchValue({ file: file });
      this.fileForm.get('file')!.updateValueAndValidity();
      this.uploadedFiles.push(file);
      this.readAndUploadFile(file);
  }

  }

  // checkValidity(){
  //   if(this.form.get('file')?.value != '' && this.form.get('file')?.value ){
  //      this.form.get('file')?.setValidators(Validators.required);
  //      this.form.get('textToDecrypt')?.setValidators(null);
  //      this.form.get('textToDecrypt')?.updateValueAndValidity();
  //      this.form.get('file')?.updateValueAndValidity();
  //      this.form.updateValueAndValidity();
  //   } else {
  //     this.form.get('textToDecrypt')?.setValidators(Validators.required);
  //     this.form.get('file')?.setValidators(null);
  //     this.form.get('file')?.updateValueAndValidity();
  //     this.form.get('textToDecrypt')?.updateValueAndValidity();
  //     this.form.updateValueAndValidity();
  //   }
  // }

  mapTextModel(){
    let formValue= this.form.getRawValue();
    const textModel= {
      key:formValue.encryptionKeySelected,
      encryptedText:this.form.value.textToDecrypt,
      encryptionAlgorithm:this.form.value.encryptionTechnique,
    };
    return textModel;
  }

  private readAndUploadFile(theFile: any) {

    // Set File Information

    (this.fileEncryptionObject as any)={};
    // Use FileReader() object to get file to upload
    // NOTE: FileReader only works with newer browsers
    let reader = new FileReader();

    // Setup onload event for reader
    reader.onload = () => {
        // Store base64 encoded representation of file
        let fileinBytes = this.convertDataURIToBinary(reader.result);
        var array = Array.from(fileinBytes)

        this.fileEncryptionObject.encryptedFileName=theFile.name;
        this.fileEncryptionObject.encryptedFileType=theFile.type;
        this.fileEncryptionObject.size=theFile.size;
        this.fileEncryptionObject.encryptedFile= array;
        this.fileEncryptionObject.key= this.form.value.encryptionKey;
        this.fileEncryptionObject.encryptionAlgorithm= this.form.value.encryptionTechnique;

        this.showFileUpload= false;
        this.showFilePendingForm= true;
        this.showFileFinishedDetails= false;
    }

    // Read the file
    reader.readAsDataURL(theFile);
}

 convertDataURIToBinary(dataURI: any) {
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

  decrypt(isFile?:boolean){

    if(isFile){
      this.fileSubmitted = true;
      if(this.fileForm.valid){
        this.fileEncryptionObject.key= this.fileForm.value.encryptionKey;
        this.fileEncryptionObject.encryptionAlgorithm= this.fileForm.value.encryptionTechnique;
        this.decryptFile(this.fileEncryptionObject);
      }
    }else{
      this.submitted = true;
      if(this.form.valid){
        const mappedModel= this.mapTextModel();
        if(mappedModel.key===''|| !mappedModel.key ){
          this.messageService.add({severity:'error', detail: 'please enter encrypted key field'});
        }else {
          this.decryptText(this.mapTextModel());
        }
      }
    }

  }

  backToUpload(){
    this.fileForm.reset();
    this.fileForm.get('encryptionKeySelected')?.enable()
    this.showFilePendingForm= false;
    this.showFileFinishedDetails= false;
    this.showFileUpload= true;
  }

   decryptFile(model: any){
    this.spinnerService.show();
    this._encryptionService.decryptFile(model).subscribe({
      next: (response) => {
        this.fileSubmitted= false
        this.downloadFile(response);
        this.spinnerService.hide();
        this.showFilePendingForm= false;
        this.showFileUpload= false;
        this.showFileFinishedDetails= true;
        this.fileUpload.clear()
      this.messageService.add({severity:'success', detail: 'data decrypted successfully'});
    },
    error: async (error) => {
        this.spinnerService.hide();
      if (error.error?.message) {
        this.messageService.add({severity:'error', detail: error.error.message});
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

  downloadFile(data: any) {
    const blob = new Blob([data], { type: data.type });
    const url= window.URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = this.fileEncryptionObject.encryptedFileName;
    link.click();
    window.open(url);
  }

  onOptionsSelected(event:any){
    if(this.form && this.form.get('encryptionKey')?.value !== 'null'){
      this.form.get('encryptionKeySelected')?.disable();
      this.form.get('encryptionKeySelected')?.setValue(this.form.get('encryptionKey')?.value);
    } else{
      this.form.get('encryptionKeySelected')?.enable();
      this.form.get('encryptionKeySelected')?.reset();
      this.form.get('encryptionKeySelected')?.setValidators(Validators.required);
      this.form.get('encryptionKeySelected')?.updateValueAndValidity();
      this.form.updateValueAndValidity();

    }
  }

  onOptionsFileSelected(event:any){
    if(this.fileForm && this.fileForm.get('encryptionKey')?.value !== '0'){
      this.fileForm.get('encryptionKeySelected')?.disable();
      this.fileForm.get('encryptionKeySelected')?.setValue(this.fileForm.get('encryptionKey')?.value);
    } else{
      this.fileForm.get('encryptionKeySelected')?.enable();
      this.fileForm.get('encryptionKeySelected')?.reset();
      this.fileForm.get('encryptionKeySelected')?.setValidators(Validators.required);
      this.fileForm.get('encryptionKeySelected')?.updateValueAndValidity();
      this.fileForm.updateValueAndValidity();
    }
  }

  decryptText(model: any){
    this.spinnerService.show();
    this._encryptionService.decryptText(model).subscribe({
      next: (response) => {
        this.spinnerService.hide();
        this.submitted= false;
        this.form.reset();
        this.form.get('decryptedText')?.setValue(response.decryptedText);
      this.messageService.add({severity:'success', detail: 'data encrypted successfully '});
    },
    error: (error) => {
        this.spinnerService.hide();

      if (error.error?.message) {
        this.messageService.add({severity:'error', detail: error.error.message});
      }
      if (error?.status === 400 && !error.error?.message) {
        this.messageService.add({severity:'error', detail: 'Encryption key for Algorithm AES is not a valid key!'});
      }
      if (error.status === 401) {
        this.messageService.add({severity:'error', detail: "Invalid credentials!"})
      }
    }


    })
  }

}

export interface FileDecryption{
  key: string;
  encryptedFile: number[];
  size: number;
  encryptedFileName: string;
  encryptedFileType: string;
  encryptionAlgorithm: string;
}

