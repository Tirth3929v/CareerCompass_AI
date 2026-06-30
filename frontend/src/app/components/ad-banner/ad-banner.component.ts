import { Component, Input, PLATFORM_ID, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';

/**
 * Placeholder component for Google AdSense banner ads.
 * Only renders in the browser (not during SSR) to avoid hydration issues.
 */
@Component({
  selector: 'app-ad-banner',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './ad-banner.component.html',
  styleUrl: './ad-banner.component.css',
})
export class AdBannerComponent {
  @Input() format: 'leaderboard' | 'rectangle' | 'sidebar' = 'leaderboard';
  @Input() slot = '';

  isBrowser: boolean;

  constructor(@Inject(PLATFORM_ID) platformId: Object) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  get containerClass(): string {
    return `ad-container ad-${this.format}`;
  }
}
