import { Injectable } from '@angular/core';
import { HttpClient, HttpRequest, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { tap, shareReplay } from 'rxjs/operators';

const HttpUploadOptions = {
headers: new HttpHeaders({ "Content-Type": "multipart/form-data" })
}

@Injectable({
  providedIn: 'root'
})
export class FileService {
	private apiRoot = 'http://127.0.0.1:8000/file/';
  constructor(private http: HttpClient) { }

  postFile(file: File, boilerplate: File, fileType): Observable<any> {
  	console.log("post file");
  	console.log(file);
    const formData: FormData = new FormData();

    formData.append('uploaded', file);
    formData.append('boilerplate', boilerplate);
    formData.append('fileType',fileType);
    console.log("hello");
	console.log("file = ",file);
	console.log("formData = ",formData);
    return this.http.post<any>(this.apiRoot.concat('upload/'), formData, {
      reportProgress: true,
      responseType: 'json',
    });
  }

	processFiles() {
		console.log("download service");
		const httpOptions = {
    			responseType: 'blob' as 'json',
	  	};

	 	return this.http.get(this.apiRoot.concat('upload/'), httpOptions);
	}
		
	getProcessedFiles() {
		console.log("download service");
		const httpOptions = {
    			responseType: 'blob' as 'json',
	  	};

	 	return this.http.get(this.apiRoot.concat('results/'), httpOptions);
	}

	getHeatMap() {
		console.log("HeatMap");
		const httpOptions = {
			responseType: 'blob' as 'json',
		};

		return this.http.get(this.apiRoot.concat('heatmap/'), httpOptions);
	}

	getHistogram() {
		console.log("Histogram");
		const httpOptions = {
			responseType: 'blob' as 'json',
		};

		return this.http.get(this.apiRoot.concat('histogram/'), httpOptions);
	}
}
