import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChallengeData } from '../../models/interfaces';

@Component({
  selector: 'app-challenge-card',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './challenge-card.component.html',
  styleUrl: './challenge-card.component.css',
})
export class ChallengeCardComponent {
  @Input() challenge!: ChallengeData;
  @Output() submitAnswer = new EventEmitter<string>();

  userAnswer = '';
  selectedOption: string | null = null;
  isSubmitted = false;
  timeRemaining = 0;
  private timerInterval: any;

  ngOnInit(): void {
    if (this.challenge?.time_limit_seconds) {
      this.timeRemaining = this.challenge.time_limit_seconds;
      this.startTimer();
    }
  }

  ngOnDestroy(): void {
    this.clearTimer();
  }

  get challengeTypeLabel(): string {
    switch (this.challenge?.type) {
      case 'code':
        return '💻 Coding Challenge';
      case 'math':
        return '🔢 Math Challenge';
      case 'logic':
        return '🧠 Logic Challenge';
      default:
        return '📝 Challenge';
    }
  }

  get challengeTypeIcon(): string {
    switch (this.challenge?.type) {
      case 'code': return '💻';
      case 'math': return '🔢';
      case 'logic': return '🧠';
      default: return '📝';
    }
  }

  get difficultyClass(): string {
    return `difficulty-${this.challenge?.difficulty || 'intermediate'}`;
  }

  get formattedTime(): string {
    const mins = Math.floor(this.timeRemaining / 60);
    const secs = this.timeRemaining % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  selectOption(option: string): void {
    if (!this.isSubmitted) {
      this.selectedOption = option;
      this.userAnswer = option;
    }
  }

  submit(): void {
    if (this.isSubmitted || !this.userAnswer.trim()) return;
    this.isSubmitted = true;
    this.clearTimer();
    this.submitAnswer.emit(this.userAnswer);
  }

  private startTimer(): void {
    this.timerInterval = setInterval(() => {
      this.timeRemaining--;
      if (this.timeRemaining <= 0) {
        this.clearTimer();
        if (!this.isSubmitted) {
          this.isSubmitted = true;
          this.submitAnswer.emit(this.userAnswer || 'TIME_EXPIRED');
        }
      }
    }, 1000);
  }

  private clearTimer(): void {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }
}
