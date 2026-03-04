import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '../shared/auth.guard';
import { LayoutComponent } from '../shared/components/layout/layout/layout.component';
import { CompanyComponent } from './components/company/company.component';
import { ContactComponent } from './components/contact/contact.component';
import { DecryptionComponent } from './components/decryption/decryption.component';
import { EncryptionComponent } from './components/encryption/encryption.component';
import { HomeComponent } from './components/home/home.component';
import { MediaComponent } from './components/media/media.component';
import { ProductsComponent } from './components/products/products.component';
import { ProfileComponent } from './components/profile/profile.component';
import { ResourcesComponent } from './components/resources/resources.component';

const routes: Routes = [
  {
    path: '',
    redirectTo: '/index',
    pathMatch: 'full',
  },
  {
    path: '',
    children: [
      { path: 'index', component: HomeComponent   },
      { path: 'company', component: CompanyComponent ,
      canActivate: [AuthGuard],
      data: { role: ['Admin', 'Employee', 'User'] },},
      { path: 'products', component: ProductsComponent,
      canActivate: [AuthGuard],
      data: { role: ['Admin', 'Employee', 'User'] }, },
      { path: 'media', component: MediaComponent,
      canActivate: [AuthGuard],
      data: { role: ['Admin', 'Employee', 'User'] }, },
      { path: 'contact', component: ContactComponent,
      canActivate: [AuthGuard],
      data: { role: ['Admin', 'Employee', 'User'] }, },
      { path: '', redirectTo: 'index', pathMatch: 'full' },
      {
        path: 'encryption',
        component: EncryptionComponent,
        canActivate: [AuthGuard],
        data: { role: ['Admin', 'Employee', 'User'] },
      },
      {
        path: 'decryption',
        component: DecryptionComponent,
        canActivate: [AuthGuard],
        data: { role: ['Admin', 'Employee', 'User'] },
      },
      {
        path: 'resources',
        component: ResourcesComponent,
        canActivate: [AuthGuard],
        data: { role: ['Admin', 'Employee'] },
      },
      {
        path: 'profile',
        component: ProfileComponent,
        canActivate: [AuthGuard],
        data: { role: ['Admin', 'Employee', 'User'] },
      },
    ],
    component: LayoutComponent,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class UserRoutingModule {}
