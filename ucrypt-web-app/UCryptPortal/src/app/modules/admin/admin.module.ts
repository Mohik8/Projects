import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AdminRoutingModule } from './admin-routing.module';
import { SharedModule } from '../shared/shared.module';
import { AccountsComponent } from './components/accounts/accounts.component';
import { RolesComponent } from './components/roles/roles.component';
import { ResourcesComponent } from './components/resources/resources.component';
import { AdminLayoutComponent } from './components/admin-layout/admin-layout.component';
import { NewAccountsComponent } from './components/new-accounts/new-accounts.component';
import { StaffAccountComponent } from './components/staff-account/staff-account.component';
import { UserAccountComponent } from './components/user-account/user-account.component';
import { AllAccountComponent } from './components/all-account/all-account.component';
import { FormsModule } from '@angular/forms';

@NgModule({
  declarations: [AccountsComponent, RolesComponent, ResourcesComponent, AdminLayoutComponent, NewAccountsComponent, StaffAccountComponent, UserAccountComponent, AllAccountComponent],
  imports: [CommonModule, AdminRoutingModule, SharedModule,FormsModule],
  exports:[FormsModule]
})
export class AdminModule {}
