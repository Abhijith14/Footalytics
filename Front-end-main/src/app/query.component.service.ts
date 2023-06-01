import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";

@Injectable()
export class QueryHttpService {
  constructor(private http: HttpClient) {}

  options = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  public query(model : any ): Observable<any> {
    return this.http.post<any>('http://localhost:5001/api/query', JSON.stringify(model), this.options);
  }
}