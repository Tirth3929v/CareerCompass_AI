import { Routes } from '@angular/router';
import { ChatComponent } from './components/chat/chat.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';

export const routes: Routes = [
  {
    path: '',
    component: ChatComponent,
    title: 'CareerCompass AI — AI Career Counselor',
  },
  {
    path: 'dashboard',
    component: DashboardComponent,
    title: 'Skill Dashboard — CareerCompass AI',
  },
  {
    path: 'dashboard/:sessionId',
    component: DashboardComponent,
    title: 'Skill Dashboard — CareerCompass AI',
  },
  {
    path: '**',
    redirectTo: '',
  },
];
