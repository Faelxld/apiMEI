package com.das.apiMEI.resources;

import com.das.apiMEI.dto.PostParam;
import com.das.apiMEI.model.Empresa;
import com.das.apiMEI.model.Pdf;
import com.das.apiMEI.repository.EmpresaRepository;
import com.das.apiMEI.repository.PdfRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/das/pdf")
public class PdfResource {
    @Autowired
    private PdfRepository repository;



    @RequestMapping(value = "/{cnpj}", method = RequestMethod.GET)
    public List<Pdf> getById(@PathVariable("cnpj") String cnpj) {

        List<Pdf> pdfs = repository.findAll();
        List<Pdf> filtro =  new ArrayList<>();

        for (Pdf pdf:pdfs) {
            if(pdf.getCnpj().equals(cnpj) && pdf.isLido()){
                filtro.add(pdf);
            }
        }
    return filtro;
    }

   
}