package com.das.apiMEI.resources;

import com.das.apiMEI.dto.PostParam;
import com.das.apiMEI.model.Empresa;
import com.das.apiMEI.repository.EmpresaRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.das.apiMEI.crawler.Crawler;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import javax.validation.Valid;
import java.io.IOException;
import java.net.URI;
import java.util.List;

@RestController
@RequestMapping("/das")
public class EmpresaResource {
    @Autowired
    private EmpresaRepository repository;

    @RequestMapping(value = "/", method = RequestMethod.GET)
    public List<Empresa> getAllPets() {
        return repository.findAll();
    }

    @RequestMapping(value = "/{cnpj}", method = RequestMethod.GET)
    public Empresa getPetById(@PathVariable("cnpj") String cnpj) {

        return repository.findBy_id(cnpj);
    }

    @RequestMapping(method=RequestMethod.POST)
    public ResponseEntity<Void> insert(@Valid @RequestBody PostParam objDto) throws IOException {
        //Executa Crawler
        final Crawler crawler = new Crawler();
        String dir = System.getProperty("user.dir");
        String cost = "/src/main/java/com/das/apiMEI/crawler";
        crawler.executeCommand("sudo python3 " +  dir + cost +"/crawler.py " + objDto.getCnpj());
        URI uri = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}").buildAndExpand(objDto.getCnpj()).toUri();
        return ResponseEntity.created(uri).build();
    }
}