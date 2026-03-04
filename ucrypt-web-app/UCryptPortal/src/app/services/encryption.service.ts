import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class EncryptionService {

  baseTextUrl = environment.apiUrl + 'encryption/text/';
  baseFileUrl = environment.apiUrl + 'encryption/file/';

  constructor(private http: HttpClient) { }


  encryptText(model: any) {
    return this.http.put<any>(this.baseTextUrl + 'encrypt', model);
  }

  public getHeaders(): HttpHeaders {
    const headers = new HttpHeaders({
      'Content-Type': '*/*'
    });
    return headers;
  }

  encryptFile(model: FormData) {

    const options = { headers: this.getHeaders() };
    const httpOptions = {
      responseType: ('blob' as 'json')
    };

    return this.http.put<any>(this.baseFileUrl + 'encrypt', model,httpOptions);
  }

  decryptText(model: any) {
    return this.http.put<any>(this.baseTextUrl + 'decrypt', model);
  }

  decryptFile(model: any) {
    const httpOptions = {
      responseType: ('blob' as 'json')
    };

    return this.http.put<any>(this.baseFileUrl + 'decrypt', model, httpOptions).pipe(
        // catchError(this.parseErrorBlob)
    )
  }

  parseErrorBlob(err: HttpErrorResponse): Observable<any> {
    const reader: FileReader = new FileReader();

    const obs = Observable.create((observer: any) => {
      reader.onloadend = (e) => {
        observer.error(JSON.parse(reader.result as any));
        observer.complete();
      }
    });
    reader.readAsText(err.error);
    return obs;
}
}
