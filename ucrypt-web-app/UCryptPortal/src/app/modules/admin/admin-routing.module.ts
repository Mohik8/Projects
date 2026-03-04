import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '../shared/auth.guard';
import { LayoutComponent } from '../shared/components/layout/layout/layout.component';
import { AccountsComponent } from './components/accounts/accounts.component';
import { AdminLayoutComponent } from './components/admin-layout/admin-layout.component';
import { ResourcesComponent } from './components/resources/resources.component';
import { RolesComponent } from './components/roles/roles.component';

const routes: Routes = [
  {
    path: '',
    children: [
      { path: 'accounts', component: AdminLayoutComponent,canActivate:[AuthGuard] , data:{role:['Admin']}},
      { path: 'resources', component: ResourcesComponent, canActivate:[AuthGuard] , data:{role:['Admin','Employee']}},
      { path: 'roles', component: RolesComponent ,canActivate:[AuthGuard], data:{role:['Admin']}},
      { path: '', redirectTo: '/index', pathMatch: 'full' },
    ],
    component: LayoutComponent,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class AdminRoutingModule {}
