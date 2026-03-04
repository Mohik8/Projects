import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SharedRoutingModule } from './shared-routing.module';
import { HeaderComponent } from './components/layout/header/header.component';
import { FooterComponent } from './components/layout/footer/footer.component';
import { LayoutComponent } from './components/layout/layout/layout.component';
import { TableModule } from 'primeng/table';
import { FileUploadModule } from 'primeng/fileupload';
import { TooltipModule } from 'primeng/tooltip';
import { HttpClientModule } from '@angular/common/http';
import {ToastModule} from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { ReactiveFormsModule } from '@angular/forms';
import { NgxSpinnerModule } from 'ngx-spinner';
import { DropdownModule } from 'primeng/dropdown';
import { LoginPageComponent } from './components/login-page/login-page.component';
import { SignUpPageComponent } from './components/sign-up-page/sign-up-page.component';


@NgModule({
  declarations: [
    HeaderComponent,
    FooterComponent,
    LayoutComponent,
    LoginPageComponent,
    SignUpPageComponent,
  ],
  imports: [
    CommonModule,
    SharedRoutingModule,
    ToastModule,
    NgxSpinnerModule,
    ReactiveFormsModule
  ],
  exports: [
    HeaderComponent,
    FooterComponent,
    LayoutComponent,
    FileUploadModule,
    TooltipModule,
    TableModule,
    DropdownModule,
    ToastModule,
    LoginPageComponent,
    SignUpPageComponent
  ],
  providers: [MessageService]
})
export class SharedModule {}
