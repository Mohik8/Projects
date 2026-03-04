import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { EncryptionAlgorithm } from '../models/encryptionAlgorithm/encryption-algorithm';

@Injectable({
  providedIn: 'root'
})
export class EncryptionAlgorithmService {
  baseUrl = environment.apiUrl ;

  constructor(private http: HttpClient) { }

  getEncryptionAlgo() {
    return this.http.get<EncryptionAlgorithm[]>(this.baseUrl + 'encryption-algorithms');

  }

  generateKey(model: any) {
    return this.http.put<any>(this.baseUrl + 'encryption-keys/generate', model);
  }

}
