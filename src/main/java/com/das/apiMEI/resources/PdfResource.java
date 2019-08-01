package com.das.apiMEI.resources;

import com.das.apiMEI.dto.PostParam;
import com.das.apiMEI.model.Empresa;
import com.das.apiMEI.model.Pdf;
import com.das.apiMEI.repository.EmpresaRepository;
import com.das.apiMEI.repository.PdfRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.das.apiMEI.crawler.Crawler;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import javax.validation.Valid;
import java.io.IOException;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/pdf")
public class PdfResource {
    @Autowired
    private PdfRepository repository;



    @RequestMapping(value = "/{cnpj}", method = RequestMethod.GET)
    public List<Pdf> getById(@PathVariable("cnpj") String cnpj) {

        List<Pdf> pdfs = repository.findAll();
        List<Pdf> filtro =  new ArrayList<>();

        for (Pdf pdf:pdfs) {
            if(pdf.getCnpj().equals(cnpj)){
                filtro.add(pdf);
            }
        }
    return filtro;
    }

    @RequestMapping(method=RequestMethod.POST)
    public ResponseEntity<Void> insert(@Valid @RequestBody PostParam objDto) throws IOException {
        //Executa Crawler
        final Crawler crawler = new Crawler();
        String dir = System.getProperty("user.dir");
        String cost = "/src/main/java/com/das/apiMEI/crawler";
        crawler.executeCommand("python3 " +  dir + "/crawler.py " + objDto.getCnpj());
        System.out.println(dir);
        URI uri = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}").buildAndExpand(objDto.getCnpj()).toUri();
        return ResponseEntity.created(uri).build();
    }
}