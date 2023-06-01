import { Component, OnInit, ViewChild } from '@angular/core';
import { Validators, FormBuilder } from '@angular/forms';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { QueryHttpService } from './query.component.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent{
  constructor(private _formBuilder: FormBuilder, private queryHttpService : QueryHttpService) {}

  firstFormGroup = this._formBuilder.group({
    firstCtrl: ['', Validators.required],
  });
  secondFormGroup = this._formBuilder.group({
    secondCtrl: ['', Validators.required],
  });
  isLinear = false;
  
  title = 'assignment3';

  nlgModelOutput : any;

  timeline : any[] = [];
  
  richSnippet: string = '';

  matchStatistics: any[] = [];

  teamALogo : string = '';
  teamBLogo : string = '';

  players: any[] = [];
  handleUserQuery($event : any){
    if ($event.code === "Enter") {
      this.queryHttpService.query($event.target.value).subscribe(response => {
        console.log(response)
        this.handleServerResponse(response);
      })
  }
}

  handleServerResponse(response : any){
    switch (response.data.event_type){
      case 'live':
        this.showLiveMatchData(response.data);
        break;
      case 'half-time':
        this.showHalfTimeData(response.data);
        break;
      case 'players-statistics':
        this.showPlayersStatistics(response.data);
        break;
    }
  }

  showLiveMatchData(response : any){
    this.timeline = response.api_response.map((response : any) => {
      console.log(response)
      return response;
    })
    this.nlgModelOutput = response.nlg_model
    this.richSnippet = 'live'
  }

  showHalfTimeData(response: any){
    this.nlgModelOutput = response.nlg_model
    response = response.api_response;
    this.richSnippet = 'half-time'
    this.teamALogo = response.statistics[0].team.logo
    this.teamBLogo = response.statistics[1].team.logo
    this.matchStatistics = [];
    this.matchStatistics.push({teama_stat: response.goals['away'], stat_type: 'Goals', teamb_stat: response.goals['home']})
    for(let i in response.statistics[0]['statistics']){
      this.matchStatistics.push({teama_stat: response.statistics[0].statistics[i].value, stat_type: response.statistics[0].statistics[i].type, teamb_stat: response.statistics[1].statistics[i].value})
    }
    console.log(response)
    this.dataSource =  new MatTableDataSource<StatElement>(this.matchStatistics);

  }

  showPlayersStatistics(response: any){
    this.richSnippet = 'players-statistics'

    console.log(response)
    this.nlgModelOutput = response.nlg_model
    this.players = response.api_response.players[0].players
  }

  mapEventToImagePath(event: string, detail : string){
    switch (event){
      case 'Goal':
        return '/assets/penalty.png';
      case 'subst':
        return '/assets/substituion.png';
      case 'Card':
        return detail === 'Yellow Card' ?  '/assets/yellow-card.png' : '/assets/red-card.png';
    }
    return '';
  }

  displayedColumns: string[] = ['teama_stat', 'stat_type', 'teamb_stat'];
  dataSource: any

 getStrippedString(str: string){
  return str.replace(/[0-9]/g, '');
 }
}

export interface StatElement {
  teama_stat: string;
  stat_type: number;
  teamb_stat: number;
}

