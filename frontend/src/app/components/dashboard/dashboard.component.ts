import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { ChatService } from '../../services/chat.service';
import { SeoService } from '../../services/seo.service';
import { SkillScore, AnalysisResult, Roadmap } from '../../models/interfaces';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit, OnDestroy {
  scores: SkillScore[] = [];
  analysis: AnalysisResult | null = null;
  roadmap: Roadmap | null = null;
  expandedPhase: number | null = null;

  private subs: Subscription[] = [];

  constructor(
    private chatService: ChatService,
    private seo: SeoService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.seo.updateForDashboard();

    this.subs.push(
      this.chatService.scores$.subscribe((scores) => {
        this.scores = scores;
      }),
      this.chatService.analysis$.subscribe((analysis) => {
        this.analysis = analysis;
        if (analysis?.target_career) {
          this.seo.updateForDashboard(analysis.target_career);
        }
      }),
      this.chatService.roadmap$.subscribe((roadmap) => {
        this.roadmap = roadmap;
        if (roadmap?.target_career) {
          this.seo.updateForRoadmap(roadmap.target_career);
        }
      })
    );
  }

  ngOnDestroy(): void {
    this.subs.forEach((s) => s.unsubscribe());
  }

  get overallScore(): number {
    return this.analysis?.overall_score || 0;
  }

  get overallScoreColor(): string {
    const score = this.overallScore;
    if (score >= 80) return 'var(--accent-secondary)';
    if (score >= 60) return 'var(--accent-primary)';
    if (score >= 40) return 'var(--accent-warning)';
    return 'var(--accent-danger)';
  }

  get scoreCircumference(): number {
    return 2 * Math.PI * 54;
  }

  get scoreDashoffset(): number {
    return this.scoreCircumference * (1 - this.overallScore / 100);
  }

  getScoreWidth(score: SkillScore): number {
    return (score.verified_score / score.max_score) * 100;
  }

  getScoreColor(score: SkillScore): string {
    const pct = (score.verified_score / score.max_score) * 100;
    if (pct >= 80) return 'var(--accent-secondary)';
    if (pct >= 60) return 'var(--accent-primary)';
    if (pct >= 40) return 'var(--accent-warning)';
    return 'var(--accent-danger)';
  }

  togglePhase(phase: number): void {
    this.expandedPhase = this.expandedPhase === phase ? null : phase;
  }

  getResourceIcon(type: string): string {
    switch (type) {
      case 'video': return '🎬';
      case 'course': return '📚';
      case 'project': return '🛠️';
      case 'book': return '📖';
      default: return '📄';
    }
  }
}
