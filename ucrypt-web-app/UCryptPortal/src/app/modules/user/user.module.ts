import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { UserRoutingModule } from './user-routing.module';
import { HomeComponent } from './components/home/home.component';
import { EncryptionComponent } from './components/encryption/encryption.component';
import { ResourcesComponent } from './components/resources/resources.component';
import { SharedModule } from '../shared/shared.module';
import { DecryptionComponent } from './components/decryption/decryption.component';
import { ProfileComponent } from './components/profile/profile.component';
import { ReactiveFormsModule } from '@angular/forms';
import { NgxSpinnerModule } from 'ngx-spinner';
import { CompanyComponent } from './components/company/company.component';
import { ProductsComponent } from './components/products/products.component';
import { MediaComponent } from './components/media/media.component';
import { ContactComponent } from './components/contact/contact.component';

@NgModule({
  declarations: [HomeComponent, EncryptionComponent, ResourcesComponent, DecryptionComponent, ProfileComponent, CompanyComponent, ProductsComponent, MediaComponent, ContactComponent],
  imports: [CommonModule, UserRoutingModule, SharedModule , NgxSpinnerModule , ReactiveFormsModule],
})
export class UserModule {}
