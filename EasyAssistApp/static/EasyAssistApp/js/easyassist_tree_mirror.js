///<reference path='../src/mutation-summary.ts'/>
var EasyAssistTreeMirror = (function () {
    function EasyAssistTreeMirror(root, delegate) {
        this.root = root;
        this.delegate = delegate;
        this.idMap = {};
    }
    EasyAssistTreeMirror.prototype.initialize = function (rootId, children) {
        this.idMap[rootId] = this.root;
        for (var i = 0; i < children.length; i++)
            this.deserializeNode(children[i], this.root);

        this.delegate.props.render_frame();
        if (this.delegate &&
            this.delegate.props &&
            this.delegate.props.add_event_listeners) {
            try {
                this.delegate.props.add_event_listeners();
            } catch(err) {
                console.error(err);
            }
        }
    };
    EasyAssistTreeMirror.prototype.applyChanged = function (removed, addedOrMoved, attributes, text) {
        var _this = this;
        // NOTE: Applying the changes can result in an attempting to add a child
        // to a parent which is presently an ancestor of the parent. This can occur
        // based on random ordering of moves. The way we handle this is to first
        // remove all changed nodes from their parents, then apply.
        addedOrMoved.forEach(function (data) {
            var node = _this.deserializeNode(data);
            var parent = _this.deserializeNode(data.parentNode);
            var previous = _this.deserializeNode(data.previousSibling);            
            if (node.parentNode)
                node.parentNode.removeChild(node);
        });
        removed.forEach(function (data) {
            var node = _this.deserializeNode(data);
            if (node.parentNode)
                node.parentNode.removeChild(node);
        });
        addedOrMoved.forEach(function (data) {
            var node = _this.deserializeNode(data);
            var parent = _this.deserializeNode(data.parentNode);
            var previous = _this.deserializeNode(data.previousSibling);
            parent.insertBefore(node, previous ? previous.nextSibling : parent.firstChild);
        });
        attributes.forEach(function (data) {
            var node = _this.deserializeNode(data);
            Object.keys(data.attributes).forEach(function (attrName) {
                var newVal = data.attributes[attrName];
                if (newVal === null) {
                    node.removeAttribute(attrName);
                }
                else {
                    if (!_this.delegate ||
                        !_this.delegate.setAttribute ||
                        !_this.delegate.setAttribute(node, attrName, newVal)) {
                        try {
                            node.setAttribute(attrName, newVal);
                        } catch(err) {}
                    }

                    /*
                        The below code is written for syncing the changes of input elements (with type of checkbox) which have been implemented using Angular. 
                        In Angular, these elements normally do not set the "checked" attribute on the input element because of which the state of the elements are not synced. 
                        Whenever a checkbox is checked, a class of "ng-valid" is set on the element which gets synced on the agent's side. 
                        When we receive this class, while updating the class attribute of this element we also set the checked value as true for that element. 
                        Similarly we receive a "ng-invalid" class for a checkbox which is unchecked
                    */
                    try {
                        let node_tag_name = node.tagName.toLowerCase();
                        let node_type = node.getAttribute("type");
                        if(node_tag_name == "input" && node_type == "checkbox") {
                            if(newVal.includes("ng-valid")) {
                                node.checked = true;
                            } else if (newVal.includes("ng-invalid")) {
                                node.checked = false;
                            }
                        }
                    } catch(err) {}
                }
            });
        });
        text.forEach(function (data) {
            var node = _this.deserializeNode(data);
            node.textContent = data.textContent;
        });
        removed.forEach(function (node) {
            delete _this.idMap[node.id];
        });

        this.delegate.props.update_edit_access(this.delegate.props.iframe);
    };
    EasyAssistTreeMirror.prototype.deserializeNode = function (nodeData, parent) {
        var _this = this;
        if (nodeData === null)
            return null;
        var node = this.idMap[nodeData.id];
        if (node)
            return node;
        var doc = this.root.ownerDocument;
        if (doc === null)
            doc = this.root;
        switch (nodeData.nodeType) {
            case Node.COMMENT_NODE:
                node = doc.createComment(nodeData.textContent);
                break;
            case Node.TEXT_NODE:
                node = doc.createTextNode(nodeData.textContent);
                break;
            case Node.DOCUMENT_TYPE_NODE:
                node = doc.implementation.createDocumentType(nodeData.name, nodeData.publicId, nodeData.systemId);
                break;
            case Node.ELEMENT_NODE:
                if (this.delegate && this.delegate.createElement)
                    node = this.delegate.createElement(nodeData.tagName);
                if (!node) {
                    if(nodeData.tagName == "svg" || nodeData.tagName == "SVG") {
                        node = doc.createElementNS("http://www.w3.org/2000/svg", nodeData.tagName);
                    } else if(parent && parent.nodeType == Node.ELEMENT_NODE && parent.closest("svg")) {
                        node = doc.createElementNS("http://www.w3.org/2000/svg", nodeData.tagName);
                    } else {
                        try {
                            node = doc.createElement(nodeData.tagName);
                        } catch(err) {
                            node = doc.createElement("easyassist_invalid_tag");
                        }
                    }
                }

                Object.keys(nodeData.attributes).forEach(function (name) {
                    if (!_this.delegate ||
                        !_this.delegate.setAttribute ||
                        !_this.delegate.setAttribute(node, name, nodeData.attributes[name])) {
                        try {
                            node.setAttribute(name, nodeData.attributes[name]);
                        } catch(err) {}
                    }
                });
                // Set Id for the later reference
                node.easyassist_element_id = nodeData.mutation_summary_id;
                break;
        }
        if (!node)
            throw "ouch";
        this.idMap[nodeData.id] = node;
        if (parent)
            parent.appendChild(node);
        if (nodeData.childNodes) {
            for (var i = 0; i < nodeData.childNodes.length; i++)
                this.deserializeNode(nodeData.childNodes[i], node);
        }
        _this.delegate.set_element_value(node, nodeData.value)
        return node;
    };
    return EasyAssistTreeMirror;
})();
var EasyAssistTreeMirrorClient = (function () {
    function EasyAssistTreeMirrorClient(target, mirror, testingQueries) {
        var _this = this;
        this.target = target;
        this.mirror = mirror;
        this.nextId = 1;
        this.knownNodes = new MutationSummary.NodeMap();
        var rootId = this.serializeNode(target).id;
        var children = [];
        for (var child = target.firstChild; child; child = child.nextSibling)
            children.push(this.serializeNode(child, true));
        this.mirror.initialize(rootId, children);
        var self = this;
        var queries = [{ all: true }];
        if (testingQueries)
            queries = queries.concat(testingQueries);
        this.mutationSummary = new MutationSummary({
            rootNode: target,
            callback: function (summaries) {
                _this.applyChanged(summaries);
            },
            queries: queries
        });
    }
    EasyAssistTreeMirrorClient.prototype.disconnect = function () {
        if (this.mutationSummary) {
            this.mutationSummary.disconnect();
            this.mutationSummary = undefined;
        }
    };
    EasyAssistTreeMirrorClient.prototype.rememberNode = function (node, id) {
        // var id = this.nextId++;
        this.knownNodes.set(node, id);
        return id;
    };
    EasyAssistTreeMirrorClient.prototype.forgetNode = function (node) {
        this.knownNodes.delete(node);
    };
    EasyAssistTreeMirrorClient.prototype.serializeNode = function (node, recursive) {
        if (node === null)
            return null;
        
        if(this.mirror.check_dom_node(node)) {
            return null;
        }

        var id = this.knownNodes.get(node);

        if (id !== undefined) {
            return { id: id };
        }
        var data = {
            nodeType: node.nodeType,
            id: this.rememberNode(node, node.__mutation_summary_node_map_id__),
            mutation_summary_id: node.__mutation_summary_node_map_id__,
        };
        switch (data.nodeType) {
            case Node.DOCUMENT_TYPE_NODE:
                var docType = node;
                data.name = docType.name;
                data.publicId = docType.publicId;
                data.systemId = docType.systemId;
                break;
            case Node.COMMENT_NODE:
            case Node.TEXT_NODE:
                data.textContent = this.mirror.obfuscate_text_node(node);
                break;
            case Node.ELEMENT_NODE:
                var elm = node;
                data.tagName = elm.tagName;
                data.attributes = {};
                data.value = this.mirror.get_element_value(elm);

                for (var i = 0; i < elm.attributes.length; i++) {
                    var attr = elm.attributes[i];
                    data.attributes[attr.name] = attr.value;
                }
                if (recursive && elm.childNodes.length) {
                    data.childNodes = [];
                    for (var child = elm.firstChild; child; child = child.nextSibling)
                        data.childNodes.push(this.serializeNode(child, true));
                }
                break;
        }
        return data;
    };
    EasyAssistTreeMirrorClient.prototype.serializeAddedAndMoved = function (added, reparented, reordered) {
        var _this = this;
        var all = added.concat(reparented).concat(reordered);
        var parentMap = new MutationSummary.NodeMap();
        all.forEach(function (node) {
            var parent = node.parentNode;
            var children = parentMap.get(parent);
            if (!children) {
                children = new MutationSummary.NodeMap();
                parentMap.set(parent, children);
            }
            children.set(node, true);
        });
        var moved = [];
        parentMap.keys().forEach(function (parent) {
            if(_this.mirror.check_dom_node(parent)) {
                return;
            }

            var children = parentMap.get(parent);
            var keys = children.keys();
            while (keys.length) {
                var node = keys[0];
                while (node.previousSibling && children.has(node.previousSibling))
                    node = node.previousSibling;
                while (node && children.has(node)) {
                    var data = _this.serializeNode(node);
                    if(data != null) {
                        data.previousSibling = _this.serializeNode(node.previousSibling);
                        data.parentNode = _this.serializeNode(node.parentNode);
                        moved.push(data);
                    }
                    children.delete(node);
                    node = node.nextSibling;
                }
                var keys = children.keys();
            }
        });
        return moved;
    };

    EasyAssistTreeMirrorClient.prototype.serializeAttributeChanges = function (attributeChanged) {
        var _this = this;
        var map = new MutationSummary.NodeMap();
        Object.keys(attributeChanged).forEach(function (attrName) {
            attributeChanged[attrName].forEach(function (element) {
                if(_this.mirror.check_dom_node(element)) {
                    return;
                }
                var record = map.get(element);
                if (!record) {
                    record = _this.serializeNode(element);
                    record.attributes = {};
                    map.set(element, record);
                }
                record.attributes[attrName] = element.getAttribute(attrName);
            });
        });
        return map.keys().map(function (node) {
            return map.get(node);
        });
    };

    EasyAssistTreeMirrorClient.prototype.applyChanged = function (summaries) {
        var _this = this;
        var summary = summaries[0];
        var removed = [];
        summary.removed.forEach(function(node) {
            var data = _this.serializeNode(node);
            if(data != null) {
                removed.push(data);
            }
        });

        // var removed = summary.removed.map(function (node) {
        //     return _this.serializeNode(node);
        // });
        var moved = this.serializeAddedAndMoved(summary.added, summary.reparented, summary.reordered);
        var attributes = this.serializeAttributeChanges(summary.attributeChanged);
        var text = summary.characterDataChanged.map(function (node) {
            var data = _this.serializeNode(node);
            data.textContent = node.textContent;
            return data;
        });
        this.mirror.applyChanged(removed, moved, attributes, text);
        summary.removed.forEach(function (node) {
            _this.forgetNode(node);
        });
    };
    return EasyAssistTreeMirrorClient;
})();
