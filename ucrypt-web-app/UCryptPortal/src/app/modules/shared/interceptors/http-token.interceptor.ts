import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { catchError, Observable, throwError } from 'rxjs';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';

@Injectable()
export class HttpTokenInterceptor implements HttpInterceptor {

  constructor(
    private router: Router,
    private messageService: MessageService

  ) {}


  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    return next.handle(request).pipe(

      catchError(
        (error:HttpErrorResponse)=>{
          if(error.status === 401){
            this.router.navigate(['/index']);
          }
          return throwError( () => error);
        }
      )
    );
  }
}
