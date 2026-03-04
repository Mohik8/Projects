import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class FileService {
  baseUrl = environment.apiUrl + 'files';

  constructor(private http: HttpClient) { }

   createFile(file:any) {
    let form = new FormData();
    form.append('file', file);
    return this.http.post<any[]>(this.baseUrl,form);
  }

  getFiles() {
    return this.http.get<any[]>(this.baseUrl);
  }

  downloadFile(filePath: string) {

    const httpOptions = {
      responseType: ('blob' as 'json'),

    };
    let RequestBody = {"filePath": filePath}; 
    return this.http.put<File>(this.baseUrl +`/download`, RequestBody, httpOptions);
  }

  deleteFile(filePath: string) {
    return this.http.delete<any>(`${this.baseUrl}/${filePath}`);
  }
}
