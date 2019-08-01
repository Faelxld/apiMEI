package com.das.apiMEI.repository;

import com.das.apiMEI.model.Empresa;
import com.das.apiMEI.model.Pdf;
import org.bson.types.ObjectId;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface PdfRepository extends MongoRepository<Pdf, String> {

    List<Pdf> findBy_id(String id);
}