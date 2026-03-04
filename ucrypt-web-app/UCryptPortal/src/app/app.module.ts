import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { SharedModule } from './modules/shared/shared.module';
import { JwtModule } from '@auth0/angular-jwt';
import { NgxSpinnerModule } from "ngx-spinner";
import { AuthGuard } from './modules/shared/auth.guard';
import { HttpTokenInterceptor } from './modules/shared/interceptors/http-token.interceptor';
import { environment } from 'src/environments/environment';

@NgModule({
  declarations: [AppComponent],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    AppRoutingModule,
    SharedModule,
    NgxSpinnerModule,
    JwtModule.forRoot({
      config: {
        tokenGetter: () => localStorage.getItem('token'),
        allowedDomains: [environment.apiDomain],
        disallowedRoutes: [
          environment.apiUrl + 'users/login',
          environment.apiUrl + 'users/register',
          environment.apiUrl + 'roles/new-users'
        ]
      }
    })
  ],
  providers: [
    AuthGuard,
    {provide:HTTP_INTERCEPTORS , useClass: HttpTokenInterceptor , multi: true}
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
